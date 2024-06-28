workflow IDEKO {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;
  define task EvaluateModel; //not sure whether we include it here

  START -> ReadData -> AddPadding -> SplitData -> TrainModel -> EvaluateModel -> END;

  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }

  configure task AddPadding {
      implementation "tasks/IDEKO/add_padding.py";
      dependency "tasks/IDEKO/src/**";
    }

  configure task SplitData {
      implementation "tasks/IDEKO/split_data.py";
      dependency "tasks/IDEKO/src/**";
  }

  configure task TrainModel {
      dependency "tasks/IDEKO/src/**";
  }

   configure task EvaluateModel {
      implementation "tasks/IDEKO/evaluate_model.py";
      dependency "tasks/IDEKO/src/**";
  }

  define data InputData;
  define data RawData;
  define data PaddedData;
  define data TrainingData;
  define data TestData;

   configure data InputData {
     path "datasets/ideko-subset/**";
   }


  InputData --> ReadData --> RawData --> AddPadding --> PaddedData --> SplitData;
  SplitData --> TrainingData;
  SplitData --> TestData;
  TrainingData --> TrainModel;
  TestData --> TrainModel;

}

workflow AW1 from IDEKO {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_nn.py";
  }
}

workflow AW2 from IDEKO {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_rnn.py";
  }
}



experiment EXP_NO_EVENTS {

    intent FindBestClassifier;

    control {
       S1 -> S2;
    }

 space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(1, 2);
        param epochs_vp = range(1, 10,2);
        param epochs_vp = enum(1);
        param epochs_vp = enum("c", "d");
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }

    }

    space S2 of AW2 {
        strategy randomsearch;
        param epochs_vp = enum(1);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

}



experiment EXP_AUTOMATED_EVENTS {

    intent FindBestClassifier;

    control {
        S1 -> E1;
        E1 ?-> S2 { condition "True"}
        E1 ?-> S3 { condition "False"}
    }

    event E1 {
        type automated;
        condition "the accuracy of the 5 lastly trained ML models is > 50%" //this we did not define but I think this should be the condition right?
        task check_accuracy_over_workflows_of_last_space;

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(80,130,10);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(80,130,5);
        param batch_size_vp = enum(64, 128, 256);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S3 of AW2 {
        strategy gridsearch;
        param epochs_vp = enum(80, 90);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
}



experiment EXP_MANUAL_EVENTS {

    intent FindBestClassifier;

    control {
        S1 -> E1 -> S2;
    }

    event E1 {
        type manual;
        task change_and_restart;
        restart True;
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
        param epochs_vp = range(90,95);
        param batch_size_vp = enum(64, 128);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }
}