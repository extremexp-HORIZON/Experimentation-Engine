workflow IDEKO {
  define task ReadData;
  define task AddPadding;
  define task SplitData;
  define task TrainModelV1;
  START -> ReadData -> AddPadding -> SplitData -> TrainModelV1 -> END;
  configure task ReadData {
      implementation "tasks/IDEKO/ReadData.py";
      dependency "tasks/IDEKO/src/**";
  }
  configure task AddPadding {
      implementation "tasks/IDEKO/AddPadding.py";
      dependency "tasks/IDEKO/src/**";
  }
  configure task SplitData {
      implementation "tasks/IDEKO/SplitData.py";
      dependency "tasks/IDEKO/src/**";
  }
  configure task TrainModelV1 {
      implementation "tasks/IDEKO/TrainModel.py";
      dependency "tasks/IDEKO/src/**";
  }
}
workflow variant-1-TrainModel from IDEKO {
  configure task TrainModelV1 {
      implementation "tasks/IDEKO/trainmodel.py";
  }
}
workflow variant-2-kO3W__nz32olBG_CUMgbI from IDEKO {
  configure task TrainModelV1 {
      implementation "tasks/IDEKO/trainmodel.py";
  }
}