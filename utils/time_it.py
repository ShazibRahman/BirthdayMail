import logging
import pathlib
import sys
import time

sys.path.append(pathlib.Path(__file__).parent.parent.resolve().as_posix())


def timeit(func):
    def wrapper(*args, **kwargs):
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        logging.info(
            f"Time taken by {func.__name__} in ({func.__module__}.py): {end_time - start_time:.6f} seconds")
        return result
    return wrapper


async def timeit_async(func):
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()

        logging.info(
            f"Time taken by {func.__name__} in ({func.__module__}.py): {end_time - start_time:.6f} seconds")
        return result
    return wrapper
