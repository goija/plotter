from __future__ import annotations


def de_bruijn_sequence(k: int, n: int) -> list[int]:
    """FKM algorithm for the lexicographically least de Bruijn sequence."""
    a = [0] * (k * n)
    sequence: list[int] = []

    def db(t: int, p: int) -> None:
        if t > n:
            if n % p == 0:
                sequence.extend(a[1 : p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return sequence


def as_word(seq: list[int]) -> str:
    return "".join(str(x) for x in seq)


def cycle_words(seq: list[int], n: int) -> list[str]:
    doubled = seq + seq[: n - 1]
    return ["".join(str(x) for x in doubled[i : i + n]) for i in range(len(seq))]
