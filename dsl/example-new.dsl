experiment EXP {

    intent FindBestClassifier;

    // ----------------------------
    // step 13
    // ----------------------------
    control {
        S1 -> E1;
        E1 ?-> S2 { condition "True"}
        E1 ?-> S3 { condition "False"}
    }

    event E1 {
        type automated;
        // event "the accuracy of the 5 lastly trained ML models is > 50%"
        task check_accuracy_over_workflows_of_last_space;
    }

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(100,105);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of AW1 {
        strategy gridsearch;
        param epochs_vp = enum(100, 110, 120);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of AW2 {
        strategy gridsearch;
        param epochs_vp = enum(100, 110, 120);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
    // ----------------------------

    // ----------------------------
    // step 14
    // ----------------------------
    control {
        S1 -> E1 -> S2;
    }

    event E1 {
        type manual;
        task reorder_next_space_if_needed; // This is fragile at this point.
    }

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(100,105);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of AW1 {
        strategy gridsearch;
        param epochs_vp = enum(100, 110, 120);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
    // ----------------------------

    space S1 of AW1 {
        strategy gridsearch; // first comes the strategy, then the parameters
        param epochs_vp = range(a, b);
        param epochs_vp = enum(1);
        param epochs_vp = range(c, d); // range(4,8,2) like in Python: the first value is included, the second not (double-check this), the third is the step
        param batch_size_vp = enum(64, 128);
        // constraint epochs_vp < batch_size_vp // just as an example

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }

    }

    space S2 of AW2 {
        strategy random;
        param epochs_vp = enum(1);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

}

assembled workflow AW1 from WF1 {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_nn.py";
  }
}

assembled workflow AW2 from WF1 {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_rnn.py";
  }
}

workflow WF1 {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;

  define operator op1;

  define metric M1 {
    datatype double;
//  type accuracy; // recall, true_positive_rate, ...
  };

  START -> ReadData -> AddPadding -> SplitData -> TrainModel  -> END;

  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }

  configure task AddPadding {
      implementation "tasks/IDEKO/add_padding.py";
      dependency "tasks/IDEKO/src/**";
      generates M1;
    }

  configure task SplitData {
      implementation "tasks/IDEKO/split_data.py";
      dependency "tasks/IDEKO/src/**";
      generates acc_model1;
  }

  configure task TrainModel {
      dependency "tasks/IDEKO/src/**";
  }

}
