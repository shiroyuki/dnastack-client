import logging

from dnastack.common.environments import env
from dnastack.common.logger import get_log_level, default_logging_level

authenticator_log_level_name = env('DNASTACK_AUTH_LOG_LEVEL',
                                   description='The log level for the authenticator. This overrides '
                                               'DNASTACK_LOG_LEVEL or the default log level.',
                                   required=False,
                                   default=None)

authenticator_log_level = get_log_level(authenticator_log_level_name) \
    if authenticator_log_level_name \
    else default_logging_level

if authenticator_log_level == logging.DEBUG:
    logging.warning('🚨 WARNING: The log level of the authenticator is set to DEBUG. At this level, it may display '
                    'highly sensitive information, such as an access token, a refresh token, a JWT. You can set the '
                    'environment variable "DNASTACK_AUTH_LOG_LEVEL" to "INFO", "WARNING", or "ERROR".')