from app.core.scheduler import SchedulerAdapter


class SchedulerService:

    def __init__(self):
        self.scheduler = SchedulerAdapter()

    async def cluster_status(self):
        return await self.scheduler.get_cluster_load()