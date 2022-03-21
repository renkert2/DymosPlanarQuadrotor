sv1 = DAEDesignSymVars(3,8,2,0,4,18);
m1 = DAEDesignModel(sv1);

sv2 = DAEDesignSymVars(1,5,1,0,1,18);
m2 = DAEDesignModel(sv2);

isequal(m1.f, m2.f)