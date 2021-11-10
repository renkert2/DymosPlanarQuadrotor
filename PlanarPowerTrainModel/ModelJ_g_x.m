function out = ModelJ_g_x(in1,in2,in3,in4)
%MODELJ_G_X
%    OUT = MODELJ_G_X(IN1,IN2,IN3,IN4)

%    This function was generated by the Symbolic Math Toolbox version 8.7.
%    09-Nov-2021 15:27:18

%None
K_Q__Propeller = in4(6,:);
K_T__Propeller = in4(7,:);
N_p__Battery = in4(8,:);
N_s__Battery = in4(9,:);
R_s__Battery = in4(12,:);
Rm__Motor = in4(13,:);
kV__Motor = in4(14,:);
u1 = in2(1,:);
u2 = in2(2,:);
x2 = in1(2,:);
x3 = in1(3,:);
mt1 = [1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,((N_p__Battery.*u1.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.*9.0e+3).*1.0e+1)./(kV__Motor.*pi.*(N_p__Battery.*3.0e+2+N_p__Battery.*Rm__Motor.*2.0e+3+N_p__Battery.*u1.^2.*9.0+N_p__Battery.*u2.^2.*9.0+N_s__Battery.*R_s__Battery.*u1.^2.*3.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*3.0e+3)),(N_p__Battery.*u1.*-9.0e+4)./(kV__Motor.*pi.*(N_p__Battery.*3.0e+2+N_p__Battery.*Rm__Motor.*2.0e+3+N_p__Battery.*u1.^2.*9.0+N_p__Battery.*u2.^2.*9.0+N_s__Battery.*R_s__Battery.*u1.^2.*3.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*3.0e+3))];
mt2 = [((N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*6.0e+3+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3).*-3.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt3 = [(sqrt(6.0).*(N_p__Battery.*2.7e+3+N_p__Battery.*Rm__Motor.*1.8e+4+N_p__Battery.*u1.^2.*8.1e+1+N_p__Battery.*u2.^2.*8.1e+1+N_s__Battery.*R_s__Battery.*u1.^2.*2.7e+4+N_s__Battery.*R_s__Battery.*u2.^2.*2.7e+4+N_p__Battery.*Rm__Motor.*u1.^2.*5.4e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*1.8e+5).*5.0)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt4 = [((N_p__Battery.*u1.*u2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.*u2.*9.0e+3).*3.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt5 = [(sqrt(6.0).*(N_p__Battery.*Rm__Motor.*u1.*u2.*5.4e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.*u2.*1.8e+5).*5.0)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt6 = [(sqrt(6.0).*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*6.0e+3+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3).*-1.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt7 = [(sqrt(6.0).*(N_p__Battery.*u1.*u2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.*u2.*9.0e+3).*1.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4)),K_T__Propeller.*x2.*2.0,K_Q__Propeller.*x2.*2.0,0.0,0.0,0.0,0.0,1.0];
mt8 = [((N_p__Battery.*u2.*2.7e+1+N_s__Battery.*R_s__Battery.*u2.*9.0e+3).*1.0e+1)./(kV__Motor.*pi.*(N_p__Battery.*3.0e+2+N_p__Battery.*Rm__Motor.*2.0e+3+N_p__Battery.*u1.^2.*9.0+N_p__Battery.*u2.^2.*9.0+N_s__Battery.*R_s__Battery.*u1.^2.*3.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*3.0e+3)),(N_p__Battery.*u2.*-9.0e+4)./(kV__Motor.*pi.*(N_p__Battery.*3.0e+2+N_p__Battery.*Rm__Motor.*2.0e+3+N_p__Battery.*u1.^2.*9.0+N_p__Battery.*u2.^2.*9.0+N_s__Battery.*R_s__Battery.*u1.^2.*3.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*3.0e+3))];
mt9 = [((N_p__Battery.*u1.*u2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.*u2.*9.0e+3).*3.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt10 = [(sqrt(6.0).*(N_p__Battery.*Rm__Motor.*u1.*u2.*5.4e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.*u2.*1.8e+5).*5.0)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt11 = [((N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*6.0e+3+N_p__Battery.*u1.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3).*-3.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt12 = [(sqrt(6.0).*(N_p__Battery.*2.7e+3+N_p__Battery.*Rm__Motor.*1.8e+4+N_p__Battery.*u1.^2.*8.1e+1+N_p__Battery.*u2.^2.*8.1e+1+N_s__Battery.*R_s__Battery.*u1.^2.*2.7e+4+N_s__Battery.*R_s__Battery.*u2.^2.*2.7e+4+N_p__Battery.*Rm__Motor.*u2.^2.*5.4e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*1.8e+5).*5.0)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt13 = [(sqrt(6.0).*(N_p__Battery.*u1.*u2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.*u2.*9.0e+3).*1.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4))];
mt14 = [(sqrt(6.0).*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*6.0e+3+N_p__Battery.*u1.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3).*-1.0e+2)./(kV__Motor.*pi.*(N_p__Battery.*9.0e+2+N_p__Battery.*Rm__Motor.*1.2e+4+N_p__Battery.*Rm__Motor.^2.*4.0e+4+N_p__Battery.*u1.^2.*2.7e+1+N_p__Battery.*u2.^2.*2.7e+1+N_s__Battery.*R_s__Battery.*u1.^2.*9.0e+3+N_s__Battery.*R_s__Battery.*u2.^2.*9.0e+3+N_p__Battery.*Rm__Motor.*u1.^2.*1.8e+2+N_p__Battery.*Rm__Motor.*u2.^2.*1.8e+2+N_s__Battery.*R_s__Battery.*Rm__Motor.*u1.^2.*6.0e+4+N_s__Battery.*R_s__Battery.*Rm__Motor.*u2.^2.*6.0e+4)),0.0,0.0,K_T__Propeller.*x3.*2.0,K_Q__Propeller.*x3.*2.0];
out = reshape([mt1,mt2,mt3,mt4,mt5,mt6,mt7,mt8,mt9,mt10,mt11,mt12,mt13,mt14],15,3);
