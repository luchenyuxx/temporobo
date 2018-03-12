# Temporobo

A robot that logs your work according your activities everyday for Neoxam JIRA.
You are free to extend it to adapt to your JIRA system.

It is very useful when your manager asks you to log your work every day and you
forget how much time did you spend on each ticket.

# Get Started

It requires Python > 3.6.

Work as daemon:
```
pip3.6 install -r requirement.txt
python3.6 robo.py -u <login>
```

or, log for specific date:

```
python3.6 robo.py -u <login> -d year-month-date
```
