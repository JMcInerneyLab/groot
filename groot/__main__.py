# noinspection PyUnresolvedReferences
import groot
import intermake


def main():
    """
    Entry point.
    We just start Intermake, which has already been configured to use Groot by `groot.__init__`.
    """
    intermake.start()


if __name__ == "__main__":
    main()
