import pprint
import sys


def check_accuracy_over_workflows_of_last_space(results):
    accuracies=[]
    print("executing check_accuracy_over_workflows_of_last_space")

    for s in results:
        # Iterating over the second-level keys (e.g., 1, 2, etc.)
        for r in results[s]:
            # Accessing the accuracy value and adding it to the list
            accuracy = results[s][r]['result']['accuracy']
            accuracies.append(accuracy)

    average_accuracy = sum(accuracies) / len(accuracies)

    print("Accuracies achieved so far: ", accuracies)

    print("The average accuracy is ", average_accuracy)

    while True:
        user_input = input("Do you want to proceed with the result (yes/no)? ").strip().lower()
        if user_input == 'yes':
            if average_accuracy > 0.50:
                return 'True'
            else:
                return 'False'
        elif user_input == 'no':
            sys.exit()
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


def change_and_restart():
    print("executing change and restart task")

    input()
    return 'True'