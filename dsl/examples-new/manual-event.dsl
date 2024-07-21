experiment Step14 {

    intent FindBestClassifier;

    control {
        //S1 -> S2 [E1 after 0.50 completion, blocking]; // blocking happens after scheduling, E1 after completion
        S1 -> E1 -> S2;
    }

    //control {
     //   S1 -> S2 || E1;
   // }

    event E1 {
        type manual;
        // the task should allow the users to change the parameters of the space and restart the spaces
        // given that workflows that are already executed are not retried, the default restarting is what we need
        task change_and_restart; // This is fragile at this point.
        restart True; // could be omitted
    }

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = range(100,105); // 100,101,102,103,104
        param batch_size_vp = enum(64, 128); // 64,128

        // order (100,64), (101,64), (102,64), (103,64), (104,64), (100,128), (101,128), (102,128), (103,128), (104,128)

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

workflow WF1 {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;

  define operator op1;

 // define metric M1 {
  //  datatype double;
//  type accuracy; // recall, true_positive_rate, ...
 // };

  START -> ReadData -> AddPadding -> SplitData -> TrainModel  -> END;

  configure task ReadData {
    implementation "tasks/IDEKO/read_data.py";
    dependency "tasks/IDEKO/src/**";
  }

  configure task AddPadding {
      implementation "tasks/IDEKO/add_padding.py";
      dependency "tasks/IDEKO/src/**";
     // generates M1;
    }

  configure task SplitData {
      implementation "tasks/IDEKO/split_data.py";
      dependency "tasks/IDEKO/src/**";
     // generates acc_model1;
  }

  configure task TrainModel {
      dependency "tasks/IDEKO/src/**";
  }

}
