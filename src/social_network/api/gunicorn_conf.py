from src.social_network import settings


social_network_settings = settings.SocialNetworkSettings()

bind = social_network_settings.server.bind
workers = social_network_settings.server.workers
# worker_class = "gunicorn.workers.UvicornWorker"
