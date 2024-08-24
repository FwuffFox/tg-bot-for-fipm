import datetime

import game

# create file
with open("results.csv", "w") as file:
    file.write(f"Группа,{",".join(game.tasks)},Сумма баллов\n")


def write_result(name: str, answers: dict[int, int]) -> None:
    with open("results.csv", "a") as file:
        file.write(f"{name},")
        file.write(
            ",".join(str(answers.get(task, 0)) for task in range(len(game.tasks)))
        )
        file.write(f",{sum(answers.values())}")
        file.write("\n")
