import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    data = open(filename,"r")
    data.readline()  # Reads the header so that it doesn't appear in dataset
    for data_row in data.readlines():
        data_row = data_row.strip()  # Gets rid of \n at the end of the line
        data_row = data_row.split(",")  # Transfroms the data to a list of evidences and label in the end
        # Indexes of headers and their data types
        # 0 Administrative / int
        # 1 Administrative_Duration / float
        # 2 Informational / int
        # 3 Informational_Duration / float
        # 4 ProductRelated / int
        # 5 ProductRelated_Duration / float
        # 6 BounceRates / float
        # 7 ExitRates / float
        # 8 PageValues / float
        # 9 SpecialDay / float
        # 10 Month / int (implemented seperately)
        # 11 OperatingSystems / int
        # 12 Browser / int
        # 13 Region / int
        # 14 TrafficType / int
        # 15 VisitorType / int (implemented seperately)
        # 16 Weekend / int (implemented seperately)
        # 17 Revenue / int (implemented seperately)
        
        for i in [0, 2, 4, 11, 12, 13, 14]:  # converts relevant indexes to integers
            data_row[i] = int(data_row[i])
        for i in [1, 3, 5, 6, 7, 8, 9]:  # converts relevant indexes to float
            data_row[i] = float(data_row[i])
        
        # Converts month to integer
        month_name = data_row[10].strip()  # Get the name of the month as a string. Remove spaces in the beginning and at the end.
        mont_dict = {"Jan":0, "Feb":1, "Mar":2, "Apr":3, "May":4, "June":5, 
                     "Jul":6, "Aug":7, "Sep":8, "Oct":9, "Nov":10, "Dec":11}
        month_index = mont_dict[month_name] 
        data_row[10] = month_index  # Update data_row s.t month is the relevant integer

        # Determines visitor_type
        visitor_type_text = data_row[15].strip()  # Removes spaces in the beginning and at the end.
        if visitor_type_text == "Returning_Visitor":
            data_row[15] = 1
        else:
            data_row[15] = 0
        
        # Determines if weekend or not
        weekend_text = data_row[16].strip()  # Removes spaces in the beginning and at the end.
        if weekend_text == "FALSE":
            data_row[16] = 0
        else:
            data_row[16] = 1

        # Determines if revenue is 1 or 0
        weekend_text = data_row[17].strip()  # Removes spaces in the beginning and at the end.
        if weekend_text == "FALSE":
            data_row[17] = 0
        else:
            data_row[17] = 1
        
        evidence.append(data_row[:-1])
        labels.append(data_row[-1])
    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence,labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    all_positives = 0
    positive_and_positively_identified = 0
    all_negatives = 0
    negative_and_negatively_identified = 0
    pair_list = list(zip(labels, predictions))  # [(labels[0], predictions[0]), (labels[1], predictions[1]),...]
    for pair in pair_list:
        if pair == (1, 1):
            all_positives += 1
            positive_and_positively_identified += 1
        elif pair == (1, 0):
            all_positives += 1
        elif pair == (0, 1):
            all_negatives += 1
        elif pair == (0, 0):
            all_negatives += 1
            negative_and_negatively_identified += 1
    
    sensitivity = positive_and_positively_identified / all_positives
    specificity = negative_and_negatively_identified / all_negatives
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
