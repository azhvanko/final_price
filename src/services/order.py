import logging
import typing as t
import uuid

import rq.exceptions
from fastapi import status
from redis.exceptions import RedisError
from rq.job import Job, JobStatus, Retry

from ..enums import (
    OrderProcessingStatus,
    OrderStatus as OrderStatusEnum,
)
from ..exceptions import HTTPException
from ..rq.processors import process_order
from ..schemas import (
    Order,
    OrderId,
    OrderStatus,
)
from .base import BaseService

__all__ = ("OrderService",)

logger = logging.getLogger(__name__)


class OrderService(BaseService):
    def create_order(self, order: Order) -> OrderId:
        job_id = uuid.uuid4()
        try:
            self.rq_queue.enqueue(
                process_order,
                job_id=str(job_id),
                order=order.model_dump(),
                **self._job_additional_params,
            )
        except RedisError:
            raise
        except Exception as e:
            logger.error(f"Failed to create order: {e}", exc_info=True)
            raise HTTPException(
                detail="Failed to create order",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return OrderId(id=job_id)

    def get_order_status(self, order_id: uuid.UUID) -> OrderStatus:
        order_status_description: str | None = None
        try:
            rq_job = self.rq_queue.fetch_job(str(order_id))
            if not rq_job:
                raise HTTPException(
                    detail="Order not found",
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            order_status, order_status_description = self._get_order_status(rq_job)
        except (HTTPException, RedisError):
            raise
        except rq.exceptions.InvalidJobOperation as e:
            logger.error(f"Invalid job operation for order {order_id}: {e}")
            return OrderStatus(
                status=OrderStatusEnum.ERROR,
                detail="Order is invalid",
            )
        except Exception as e:
            logger.error(f"Error fetching order status: {e}", exc_info=True)
            order_status = OrderStatusEnum.ERROR
        return OrderStatus(
            status=order_status,
            detail=order_status_description or order_status.description,
        )

    @property
    def _job_additional_params(self) -> dict[str, t.Any]:
        result: dict[str, t.Any] = {
            "job_timeout": self.config.rq_job_timeout,
            "result_ttl": self.config.rq_job_result_ttl,
            "failure_ttl": self.config.rq_job_failure_ttl,
        }
        if self.config.rq_job_retry:
            result["retry"] = Retry(self.config.rq_job_retry_count)
        return result

    @staticmethod
    def _get_order_status(rq_job: Job) -> tuple[OrderStatusEnum, str | None]:
        rq_job_status: JobStatus = rq_job.get_status()
        match rq_job_status:
            case (
                JobStatus.CREATED |
                JobStatus.DEFERRED |
                JobStatus.QUEUED |
                JobStatus.SCHEDULED |
                JobStatus.STARTED
            ):
                return OrderStatusEnum.PROCESSING, None
            case JobStatus.CANCELED | JobStatus.FAILED | JobStatus.STOPPED:
                return OrderStatusEnum.ERROR, None
            case JobStatus.FINISHED:
                rq_job_return_value = rq_job.return_value()
                if rq_job_return_value:
                    order_processing_status = rq_job_return_value.get("status", None)
                    if order_processing_status == OrderProcessingStatus.ACCEPTED:
                        return OrderStatusEnum.ACCEPTED, None
                    return OrderStatusEnum.REJECTED, rq_job_return_value.get("detail", None)
                return OrderStatusEnum.REJECTED, None
