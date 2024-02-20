from rq import Worker as RQWorker

from dotenv import load_dotenv

from .app import create_app


class Worker(RQWorker):

    def work(self, *args, **kwargs):
        load_dotenv()

        app = create_app()

        with app.app_context():
            super().work(*args, **kwargs)
