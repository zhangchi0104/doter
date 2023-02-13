# from joblib import Parallel, delayed
# from rich.console import Console
# from rich.status import Status
# from time import monotonic
# import asyncio as aio
#
#
# async def ui_worker(queue: aio.Queue):
#     while True:
#         item = await queue.get()
#         print(item)
#         queue.task_done()
#
#
# async def rich_job(job_id: str, queue: aio.Queue):
#     for i in range(4):
#         queue.put_nowait({"job": job_id, "step": i})
#         await aio.sleep(1)
#
#
# async def main():
#     start = monotonic()
#     q = aio.Queue()
#     aio.create_task(ui_worker(q))
#     tasks = [rich_job(str(i), q) for i in range(4)]
#     await aio.gather(*tasks)
#
#     end = monotonic()
#     print(f"Done in {end-start:.2f}s")
#
#
# if __name__ == "__main__":
#     aio.run(main())
from typing import TypeVar, Generic,get_args

A = TypeVar("A")
B = TypeVar("B")

class BaseClass(Generic[A, B]):
    pass


class ChildClass(BaseClass[int, str]):
    pass

print(get_args(ChildClass.__orig_bases__[0])[1])