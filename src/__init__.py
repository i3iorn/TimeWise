# Import cprofiler
import cProfile
import pstats

if __name__ == '__main__':
    profiler = cProfile.Profile()

    profiler.enable()

    from src.timewise import TimeWise

    app = TimeWise()
    task = app.add_task("MyFirstTask")

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('tottime').print_stats(10)
