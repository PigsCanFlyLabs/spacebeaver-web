from enum import Enum


class OnboardingStepsEnum(Enum):
    SIGN_UP = 0
    # DETAILS = 2
    # ADD_DEVICE = 3
    # PICK_PLAN = 4
    # PAYMENT = 5
    # ACTIVATION = 6
    DETAILS = 1
    ADD_DEVICE = 2
    PICK_PLAN = 3
    PAYMENT = 4


class ProfileStepsEnum(Enum):
    DASHBOARD = 1
    BILLING = 2
    SETTINGS = 3


class STRIPE_PLAN_PERIOD(Enum):
    ONETIME = "onetime"
    DAILY = "day"
    WEEKLY = "week"
    MONTHLY = "month"
    YEARLY = "year"
