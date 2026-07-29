# The screen's dictionary contains the objects of the models and controllers
# of the screens of the application.

from Model.main_screen import MainScreenModel
from Controller.main_screen import MainScreenController
from Model.onboarding_screen import OnboardingScreenModel
from Controller.onboarding_screen import OnboardingScreenController
from Model.common_screen import CommonScreenModel
from Controller.common_screen import CommonScreenController

screens = {
    'main screen': {
        'model': MainScreenModel,
        'controller': MainScreenController,
    },
    'common screen': {
        'model': CommonScreenModel,
        'controller': CommonScreenController,
    },
    'onboarding screen': {
        'model': OnboardingScreenModel,
        'controller': OnboardingScreenController,
    },
}
