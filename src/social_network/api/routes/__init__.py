from src.social_network.api.routes.docs import add_documentation_route
from src.social_network.api.routes.login import router as login_router
from src.social_network.api.routes.user import router as user_router


__all__ = [
    "add_documentation_route",
    "login_router",
    "user_router",
]
