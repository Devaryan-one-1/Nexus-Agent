from app.agent import Decision

def test_task_decision():
    d = Decision(action='delegate', reply='Queued', title='Draft brief',
                 description='Outline the project', priority=2, agent='planning')
    assert d.priority == 2
    assert d.agent == 'planning'
