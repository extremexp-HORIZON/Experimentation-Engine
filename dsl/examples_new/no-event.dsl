workflow WF1 {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;

  define operator op1;

  START -> ReadData -> AddPadding -> SplitData -> TrainModel  -> END;

  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }

  configure task AddPadding {
      implementation "tasks/IDEKO/add_padding.py";
      dependency "tasks/IDEKO/src/**";
      //generates M1;
    }

  configure task SplitData {
      implementation "tasks/IDEKO/split_data.py";
      dependency "tasks/IDEKO/src/**";
      //
  }

  configure task TrainModel {
      dependency "tasks/IDEKO/src/**";
  }

}


workflow AW1 from WF1 {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_nn.py";
  }
}

workflow AW2 from WF1 {
  configure task TrainModel {
      implementation "tasks/IDEKO/train_rnn.py";
  }
}



experiment EXP1 {

    intent FindBestClassifier;

    control {
       S1 -> S2;
    }

 space S1 of AW1 {
        strategy gridsearch; // first comes the strategy, then the parameters
        param epochs_vp = range(1, 2);
        param epochs_vp = enum(1);
        param epochs_vp = enum("c", "d"); // range(4,8,2) like in Python: the first value is included, the second not (double-check this), the third is the step
        param batch_size_vp = enum(64, 128);
        // constraint epochs_vp < batch_size_vp // just as an example

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


experiment EXP2 {}