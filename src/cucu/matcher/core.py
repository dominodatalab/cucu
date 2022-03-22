#
# cucu's matching sub system which allows for a pluggable matching architecture
#

# WIP:  thinking of how to generalize the idea of finding elements on the
#       currently opened browser while also being able to handle opening
#       browsers through selenium, cypress or whatever.


class ElementMatcher:
    def __init__(self):
        pass

    def find_button(self, execute_script, name, index: 0):
        """
        return the button labeled by the name provided and use the index to
        pick a specific one if there are duplicates.

        arguments:
            execute_script - function to execute javascript in the currently
                             running browsers javascript console.
            name           - name of the button we want to find on screen.
            index          - 0-base index of which element to return if there
                             are duplicates. default: 0

        return:
            return the Element found

        """
        raise RuntimeError("implement me")
