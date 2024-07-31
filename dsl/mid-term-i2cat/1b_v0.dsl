workflow I2CAT_V1 {

  define task ReadData;
  define task SplitDataset;
  define task Modelling;
  START -> ReadData -> SplitDataset -> Modelling -> END;

  configure task ReadData {
    implementation "tasks/I2CAT/Binary_v0/read_data.py";
    dependency "tasks/I2CAT/Binary_v0/utils/**";
  }


  configure task SplitDataset {
    implementation "tasks/I2CAT/Binary_v0/split_dataset.py";
    dependency "tasks/I2CAT/Binary_v0/utils/**";
  }

  configure task Modelling {
    dependency "tasks/I2CAT/Binary_v0/utils/**";
  }


  define data InputData;

  configure data InputData {
    path "datasets/v0/**";
  }

  InputData --> ReadData;

}


workflow AW1 from I2CAT_V1 {
  configure task Modelling {
      implementation "tasks/I2CAT/Binary_v0/modelling.py";
  }
}

experiment EXP {

    intent FindBestClassifier;

    control {
        S1 -> E1;
    }

    space S1 of AW1 {
        strategy gridsearch;
        param epochs_vp = enum(2);
        param batch_size_vp = enum(64);

        configure task Modelling {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    event E1 {
        type automated;
        condition "the accuracy of the 5 lastly trained ML models is > 50%";
        task check_accuracy_over_workflows_of_last_space;
    }

}
