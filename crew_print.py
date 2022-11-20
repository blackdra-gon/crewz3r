from crew_tasks import Task, SpecialTask
from crew_types import CardDistribution, Card
from crew_utils import CrewGameState

COLOUR_NAMES = ('R', 'G', 'B', 'Y', 'P', 'N', 'X')

# Parameters determining the formatting of table output.
table_elements: dict[str, str] = {
    'column_separator': ' | ',
    'player_prefix': 'Player ',
    'trick_start_marker': '>',
    'task_completion_marker': '*',
}

# Rules for the formatting of table output.
table_formatting_rules: dict[str, bool] = {
    'mark_trick_start': True,
    'mark_task_completion': True,
}

# Widths of table elements.
table_element_widths: dict[str, int] = {
    'colour_name': max(map(len, COLOUR_NAMES)),
    'card_value': 1,
    'trick_start_marker':
        len(table_elements['trick_start_marker'])
        if table_formatting_rules['mark_trick_start'] else 0,
    'task_completion_marker':
        len(table_elements['task_completion_marker'])
        if table_formatting_rules['mark_task_completion'] else 0,
}


def card_string(card: Card):
    width = table_element_widths["colour_name"]
    return (f'({COLOUR_NAMES[card[0]]:{width}} '
            f'{card[1]:>{table_element_widths["card_value"]}})')


def print_card_distribution(cards: CardDistribution):
    for i, cs in enumerate(cards):
        print(f'{table_elements["player_prefix"]}'
              f'{i + 1}:', end=' ')
        print(', '.join([card_string(c) for c in cs]))


def print_tasks(tasks: list[Task | SpecialTask]):
    print_regular_tasks([t for t in tasks if type(t) == Task])
    print_special_tasks([t for t in tasks if type(t) == SpecialTask])


def print_regular_tasks(tasks: list[Task]):
    ordered_tasks = []
    last_task = None
    for task in tasks:
        print(f'Task for {table_elements["player_prefix"]}'
              f'{task.player}: {card_string(task.card)}')
        if task.order_constraint > 0:
            ordered_tasks.append(task)
        elif task.order_constraint == -1:
            last_task = task
    if ordered_tasks:
        ordered_tasks.sort(key=lambda task: task.order_constraint)
        # Only one type of constraint can exist, check on first element.
        if ordered_tasks[0].relative_constraint:
            # The game is using relative constraints
            for i, o_task in enumerate(ordered_tasks[:-1]):
                print('Task order constraint (relative): '
                      f'{card_string(o_task.card)} must be completed '
                      f'before {card_string(ordered_tasks[i + 1].card)}.')
        else:
            # The game is using absolute constraints
            for i, o_task in enumerate(ordered_tasks[:-1]):
                print('Task order constraint (absolute): '
                      f'{card_string(o_task.card)} must be number {i + 1} '
                      f'in the order of all {len(tasks)} completed tasks.')
    if last_task:
        print('Task order constraint (absolute): '
              f'{card_string(last_task.card)} '
              f'must be the last task to be completed.')


def print_special_tasks(tasks: list[SpecialTask]):
    for task in tasks:
        print(f'Special task: {task.description}')


def print_initial_game_state(game_state: CrewGameState):
    print('\nCard distribution:')
    print_card_distribution(game_state.hands)
    print('\nTasks:')
    print_tasks(game_state.tasks)
