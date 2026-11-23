# Tables in the article

Source for `viz.py tables article/tables.md results/figures/table`, which draws them as images for Medium
(Medium has no tables). Bold marks the best of each model's settings.

| Model ("xhigh") | Finished a network | Median score | Best score |
| --------------- | ------------------ | ------------ | ---------- |
| Haiku 5.5       | 0 of 10            | 0.54         | 0.54       |
| Sonnet 5.5      | 6 of 10            | 29           | 351        |
| **Opus 5.5**    | 4 of 10            | 0.54         | **510**    |
| Fable 5.2       | 0 of 10            | 0.54         | 0.54       |

| Model      | Setting | Finished a network | Median score | Best score |
| ---------- | ------- | ------------------ | ------------ | ---------- |
| Haiku 5.5  | medium  | **5 of 5**         | 5.3          | 7.8        |
| Haiku 5.5  | high    | 9 of 10            | **6.4**      | **20**     |
| Haiku 5.5  | xhigh   | 0 of 10            | 0.54         | 0.54       |
| Sonnet 5.5 | high    | **10 of 10**       | 7.6          | 16         |
| Sonnet 5.5 | xhigh   | 6 of 10            | **29**       | **351**    |
| Sonnet 5.5 | max     | 0 of 5             | 0.54         | 0.54       |
| Opus 5.5   | medium  | **5 of 5**         | 41           | 109        |
| Opus 5.5   | high    | **10 of 10**       | **56**       | 352        |
| Opus 5.5   | xhigh   | 4 of 10            | 0.54         | **510**    |
| Opus 5.5   | max     | 0 of 5             | 0.54         | 0.54       |
| Fable 5.2  | medium  | **5 of 5**         | 61           | 119        |
| Fable 5.2  | high    | 9 of 10            | **450**      | **503**    |
| Fable 5.2  | xhigh   | 0 of 10            | 0.54         | 0.54       |

| Network                           | Score | Misses per ball |
| --------------------------------- | ----- | --------------- |
| Fable, best ("high")              | 503   | 1 in 2,100      |
| Opus, best ("xhigh")              | 510   | 1 in 1,800      |
| GPT-6 Astra                       | 503   | 1 in 900        |
| Opus, worst finished ("xhigh")    | 57    | 1 in 95         |
| "Move the paddle toward the ball" | 8     | 1 in 10         |
