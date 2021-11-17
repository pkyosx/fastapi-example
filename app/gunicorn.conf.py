bind = '0.0.0.0:80'
worker_class = "uvicorn.workers.UvicornWorker"
threads = 100
loglevel = 'info'


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    worker.log.exception("worker received INT or QUIT signal")


def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
