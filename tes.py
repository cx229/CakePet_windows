import queue


def func(tasks):
    for i, t in enumerate(tasks):
        t.append(i)  # 增加序号
    tasks.sort()

    a_tasks = []
    res = []

    t = 1
    index = 0

    for task in tasks:
        if task[0] < t:
            a_tasks.append([-task[1], -task[2]])
        else:  # 任务结束，
            if len(a_tasks) > 0:  # 之前有堆积冷雾
                a_tasks.sort()
                res.append(-a_tasks[-1][1])
                t += -a_tasks[-1][-1]
                a_tasks.pop()

            else:  # 无堆积任务，直接完成当前任务
                res.append(task[2])
                t += task[1]

    a_tasks.sort()
    for task in a_tasks[::-1]:  # 剩余的，都以及倒序排列了
        res.append(-task[1])

    return res


tasks = [[1, 4], [2, 2], [3, 1]]

tasks = [[0, 2], [0, 1], [0, 3]]

res = func(tasks)
print(res)


def xx(x):
    print(x)

res = 1
class Test:
    def __init__(self, tasks):
        c= True
        for i in range(10):
            print(i)

        print(c)

        self.tasks = tasks
        x = 0
        self.res = func(tasks)


    def test_func(self):
        tasks = [[1, 4], [2, 2], [3, 1]]
        res = func(tasks)
        assert res == [0, 2, 1, 3]
    def yy(self,x):
        assert self.res[self.index] == self.tasks[self.index][2]
        self.index += x
