from datetime import datetime
from typing import Callable
from dateutil.parser import parse
from ..expression_evaluator import ExpressionEvaluator, EvaluateExpressionDelegate
from ..expression_type import FORMATDATETIME
from ..function_utils import FunctionUtils
from ..return_type import ReturnType


class FormatDateTime(ExpressionEvaluator):
    def __init__(self):
        super().__init__(
            FORMATDATETIME,
            FormatDateTime.evaluator(),
            ReturnType.String,
            FormatDateTime.validator,
        )

    @staticmethod
    def evaluator() -> EvaluateExpressionDelegate:
        def anonymous_function(args: list):
            result: object = None
            error: str = None
            timestamp = args[0]
            if isinstance(timestamp, str):

                def anonymous_func(date_time: datetime):
                    if len(args) == 2:
                        return date_time.strftime(args[1])
                    return (
                        date_time.strftime(FunctionUtils.default_date_time_format)[:-4]
                        + "Z"
                    )

                result, error = FormatDateTime.parse_time_stamp(
                    timestamp, anonymous_func
                )
            elif isinstance(timestamp, datetime):
                if len(args) == 2:
                    result = timestamp.strftime(args[1])
                else:
                    result = (
                        timestamp.strftime(FunctionUtils.default_date_time_format)[:-4]
                        + "Z"
                    )
            else:
                error = (
                    "formatDateTime has invalid first argument {" + str(timestamp) + "}"
                )
            return result, error

        return FunctionUtils.apply_with_error(anonymous_function)

    @staticmethod
    def parse_time_stamp(
        timestamp: str, transform: Callable[[datetime], object] = None
    ):
        result: object = None
        error: str = None
        parsed = None
        try:
            parsed = parse(timestamp)
            result = transform(parsed) if transform is not None else parsed
        except:
            error = "Could not parse {" + timestamp + "}"
        return result, error

    @staticmethod
    def validator(expression: object):
        FunctionUtils.validate_order(expression, [ReturnType.String], ReturnType.Object)
