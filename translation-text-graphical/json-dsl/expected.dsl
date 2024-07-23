package IDEKO;

workflow IDEKO_main {

  define task ReadData;
  define task PrepareData;
  define task TrainModel;
  define task EvaluateModel;

  // Task CONNECTIONS
  START -> ReadData -> PrepareData -> TrainModel -> EvaluateModel -> END;

  configure task ReadData {
    implementation "IDEKO-task-library.ReadIDEKOData";
  }

  configure task PrepareData {
    implementation "IDEKO-experiment1.IDEKO_DataPreprocessing";
  }

  configure task EvaluateModel {
    implementation "IDEKO-task-library.EvaluateModel";
  }

  // DATA
  define input data ExternalDataFile;

  configure data ExternalDataFile {
    path "datasets/ideko-subset/**";
  }

}

workflow variant-1-TrainModel from IDEKO_main {

  configure task TrainModel {
    implementation "IDEKO-task-library.TrainModelNN";
  }

}

workflow variant-2-kO3W__nz32olBG_CUMgbI from IDEKO_main {

  configure task TrainModel {
    implementation "IDEKO-task-library.TrainModelRNN";
  }

}

experiment EXP {

    intent FindBestClassifier;

    control {
        //Automated
        S1
    }

    space S1 of variant-1-TrainModel {
        strategy gridsearch;
        param epochs_vp = range(2,4);
        param batch_size_vp = enum(64);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

    space S2 of variant-2-kO3W__nz32olBG_CUMgbI {
        strategy gridsearch;
        param epochs_vp = range(2);
        param batch_size_vp = enum(32);

        configure task TrainModel {
             param epochs = epochs_vp;
             param batch_size = batch_size_vp;
        }
    }

}

workflow IDEKO_DataPreprocessing {

  define task AddPadding;
  define task SplitData;

  START -> AddPadding -> SplitData -> END;

  configure task AddPadding {
    implementation "IDEKO-task-library.AddPaddingTask"
  }

  configure task SplitData {
    implementation "extremexp-mltask-library.PrepareData.SplitData"
  }

}