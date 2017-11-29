# noinspection PyUnresolvedReferences
import groot
import intermake


print( "groot " * int( groot.__version__.split( "." )[-1] ) )


def main():
    """
    Entry point.
    """
    intermake.start()


if __name__ == "__main__":
    main()
