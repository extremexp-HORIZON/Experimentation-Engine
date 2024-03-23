workflow BinaryClassificationModel {

  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModel;

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

  START -> ReadData -> AddPadding -> SplitData -> TrainModel -> END;

  define data ReadDataInput;

  configure data ReadDataInput {
     path "datasets/ideko-subset/**";
  }

  ReadDataInput --> ReadData;

}

//workflow W3 {
//  define task TestSubWorkflowTask1;
//  define task TestSubWorkflowTask2;
//
//  START -> TestSubWorkflowTask1 -> TestSubWorkflowTask2 -> END;
//}

workflow TrainingAndEvaluation {

  define task CreateCompileFitModel;
  define task EvaluateModel;
  // define task TestA;

  define data TrainingData2;
  define data TestData2;
  define data FittedMLModel;

  START -> CreateCompileFitModel -> EvaluateModel;
  // START -> CreateCompileFitModel -> TestA -> EvaluateModel;
  EvaluateModel -> END;

  //configure task TestA {
  //  implementation W3;
  //}

  CreateCompileFitModel --> FittedMLModel --> EvaluateModel;

  TrainingData --> CreateCompileFitModel;

  TrainingData --> EvaluateModel;
  TestData --> EvaluateModel;

}



assembled workflow ΝΝClassificationModel from BinaryClassificationModel {
    configure task TrainModel {
        configure task CreateCompileFitModel {
            implementation "nn.py";
        }
    }
}

assembled workflow RΝΝClassificationModel from BinaryClassificationModel {
    configure task TrainModel {
        configure task CreateCompileFitModel {
            implementation "rnn.py";
        }
    }
}

espace NNExpSpace of ΝΝClassificationModel {

    configure self {
        method gridsearch as g;
        g.epochs_vp = enum(40,50);
        g.batch_size_vp = enum(54,64);

    //    method randomsearch as r {runs = 4};
    //    r.epochs_vp = range([45,55]);
    //    r.batch_size_vp = range([55,75]);
    }

    task CreateCompileFitModel{
        param epochs = g.epochs_vp;
        param batch_size = g.batch_size_vp;

     //   param epochs = r.epochs_vp;
     //   param batch_size = r.batch_size_vp;
    }

}
