"""Common conditional-regression interface and network construction."""

from torch import nn


def mlp(d, width, out, depth=2):
    layers = []
    for _ in range(depth):
        layers += [nn.Linear(d, width), nn.GELU()]
        d = width
    return nn.Sequential(*layers, nn.Linear(d, out))


class conditional_model(nn.Module):

    def loss(self, episode):
        return (
            -self.predict(episode.context, episode.query)
            .log_prob(episode.target)
            .mean()
        )
