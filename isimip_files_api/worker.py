from rq import Worker as RQWorker

from .app import create_app


class Worker(RQWorker):

    def work(self, *args, **kwargs):
        app = create_app()

        with app.app_context():
            super().work(*args, **kwargs)
