workflow IDEKO_V1 {
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

}

