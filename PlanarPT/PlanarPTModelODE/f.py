from numpy import *

def f(x,u,d,theta):
# auto-generated function from matlab

	x2 = x[1]
	x3 = x[2]
	u1 = u[0]
	u2 = u[1]
	theta2 = theta[1]
	theta3 = theta[2]
	theta4 = theta[3]
	theta5 = theta[4]
	theta6 = theta[5]
	theta7 = theta[6]
	theta8 = theta[7]
	theta9 = theta[8]
	theta10 = theta[9]
	theta11 = theta[10]
	theta13 = theta[12]
	out1 = (6945*(4398059404710355075*theta5*u1*x2 + 4398059404710355075*theta5*u2*x3 - 1704084693378400256*theta5*theta6*theta11*u1**2 - 1704084693378400256*theta5*theta6*theta11*u2**2))/(2878521441517568*theta5*theta8*theta11*(400000*theta5 + 2666689*theta5*theta10 + 12000*theta5*u1**2 + 12000*theta5*u2**2 + 4000000*theta6*theta9*u1**2 + 4000000*theta6*theta9*u2**2)) 
	out2 = -((18914341405592543608037567138671875*(1759223761884142030000000*theta5*x2 + 52776712856524260900000*theta5*u2**2*x2 + 11728256635887652064596675*theta5*theta10*x2 - 681633877351360102400000*theta5*theta6*theta11*u1 - 52776712856524260900000*theta5*u1*u2*x3 + 17592237618841420300000000*theta6*theta9*u2**2*x2 - 4544263906900552800272384*theta5*theta6*theta10*theta11*u1 - 17592237618841420300000000*theta6*theta9*u1*u2*x3))/(228059964569348325720861368897630509463502848*theta11*(160000000000*theta5 + 2133351200000*theta5*theta10 + 7111230222721*theta5*theta10**2 + 4800000000*theta5*u1**2 + 4800000000*theta5*u2**2 + 32000268000*theta5*theta10*u1**2 + 1600000000000*theta6*theta9*u1**2 + 32000268000*theta5*theta10*u2**2 + 1600000000000*theta6*theta9*u2**2 + 10666756000000*theta6*theta9*theta10*u1**2 + 10666756000000*theta6*theta9*theta10*u2**2)) + (3078954507600442568115234375*theta2**5*theta7*theta11*theta13*x2**2)/633825300114114700748351602688)/(theta11*(theta3 + theta4)) 
	out3 = -((18914341405592543608037567138671875*(1759223761884142030000000*theta5*x3 + 52776712856524260900000*theta5*u1**2*x3 + 11728256635887652064596675*theta5*theta10*x3 - 681633877351360102400000*theta5*theta6*theta11*u2 - 52776712856524260900000*theta5*u1*u2*x2 + 17592237618841420300000000*theta6*theta9*u1**2*x3 - 4544263906900552800272384*theta5*theta6*theta10*theta11*u2 - 17592237618841420300000000*theta6*theta9*u1*u2*x2))/(228059964569348325720861368897630509463502848*theta11*(160000000000*theta5 + 2133351200000*theta5*theta10 + 7111230222721*theta5*theta10**2 + 4800000000*theta5*u1**2 + 4800000000*theta5*u2**2 + 32000268000*theta5*theta10*u1**2 + 1600000000000*theta6*theta9*u1**2 + 32000268000*theta5*theta10*u2**2 + 1600000000000*theta6*theta9*u2**2 + 10666756000000*theta6*theta9*theta10*u1**2 + 10666756000000*theta6*theta9*theta10*u2**2)) + (3078954507600442568115234375*theta2**5*theta7*theta11*theta13*x3**2)/633825300114114700748351602688)/(theta11*(theta3 + theta4)) 

	return out1, out2, out3
