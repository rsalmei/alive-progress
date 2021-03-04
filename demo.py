import time

from alive_progress import alive_bar
from alive_progress.tools.sampling import OVERHEAD_SAMPLING

cases = [
    (5000, dict(total=5000, manual=False, title='Normal auto')),
    (4000, dict(total=6000, manual=False, title='Underflow auto')),
    (4000, dict(total=4000, manual=False, title='Overflow auto')),
    (5000, dict(total=0, manual=False, title='Unknown auto')),
    (5000, dict(total=5000, manual=True, title='Normal manual')),
    (4000, dict(total=6000, manual=True, title='Underflow manual')),
    (4000, dict(total=4000, manual=True, title='Overflow manual')),
    (5000, dict(total=0, manual=True, title='Unknown manual')),
    # (5000, dict(total=..., manual=False, title='Calculating auto')),
    # (5000, dict(total=..., manual=True, title='Calculating manual')),
]

for total, case in cases:
    with alive_bar(title_length=16, **case) as bar:
        # bar.text('Quantifying...')
        # time.sleep(0)
        bar.text('Processing...')
        time.sleep(0)
        # bar.reset(total)
        if case['manual']:
            for i in range(1, total + 1):
                time.sleep(.00015)
                bar((float(i) / total))
        else:
            for i in range(1, total + 1):
                time.sleep(.0005)
                bar()
                # if i and i%3800==0: print('nice')
print()

for name, config in OVERHEAD_SAMPLING:
    with alive_bar(5000, title_length=16, title=name, **config) as bar:
        # bar.text('Quantifying...')
        # time.sleep(0)
        bar.text('Processing...')
        time.sleep(0)
        # bar.reset(total)
        for i in range(1, 5001):
            time.sleep(.0005)
            bar()
            # if i and i%3800==0: print('nice')
        bar.text('Ok, done!')
print()
