import numpy as np
import sys
import pandas as pd

T = 1000  # periods
nt = 4  # number of periods (quarters)
Nfirms = 100
n_montecarlo = 1
ans_test_r = 1
umin = 0  # related to the production
umax = 2
beta = 0.02  # formula interest rate
bb = 2  # beta Bernoulli % 2 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PLAY WITH
# srd=0.00001; % sigma de RD, BOT 0.00001
phi_entry = 0.1  # productivity entry of new firms
d1 = 0  # minimum growth rate phi (productivity)% 0 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PLAY WITH
d2 = 0.02  # maximum growth rate phi (productivity %0.02 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PLAY WITH
# d1=0.1; d2=0.15; mas o menos
g = 1.1  # cost ; 1.3
phi = 0.1
nu = 0.08
alpha_r = 0.5
lambda_val = 0
theta = 0
omega = 0.002
share_K = 0.5
bar = 0.01
bar_max = 0.1
K_entry = 5
min_K = K_entry / 2
A_entry = 1  # eN EL PAPER ES NET WORTH, E
A_exit = 0
L_entry = 4
initial_equity_ratio = A_entry / K_entry
ans_mode = 2
ans_record = 1
ans_write_gab = 1
ans_iCopertura = 1
ans_cash = 1
share_cash = 0.03
c = 1  # %%%% b en nuevo tex
ki = 1  # %%%% kapital intensity
wage = 0.005  # %%%% real wage ¿cuanto deberia representar wage respecto gr?


# gamma = (w / ki) + g * r[:, 0]

# PLAY WITH
plots_casestudy = 1  # SI 1 hace los plots respecto una montecarlo. solo usar para un caso especifico
plots_casestudy_TODO = 0  # SI 1 hace todos los gráficos del case study, si 0 solo main variables
rstd = 1
pd2 = 45  # 80, 85 % with O_phi 4 (minimum percentile)
pd1 = 82  # 50, 15 % with O_phi 4 (maximum percentile)
# O_phi = 3  # Choice for the productivity of the entry firm at time t
# 3 (fixed), 5 (std around median
# credit_mode = 1
# 1, credit is based on RD, 2 credit is based on phi

# directory_gab = 'C:\\Users\\DAVID\\Dropbox\\1_GATIGAB\\resultados_elasticity\\montecarlo\\'
# directory_plot = 'C:\\Users\\DAVID\\Dropbox\\1_GATIGAB\\resultados_elasticity\\figures\\case_study\\'
directory_gab = 'montecarlo'
directory_plot = 'case_study'

s = np.ceil(np.round(np.random.rand(1, n_montecarlo) * 100))

# a = st[(st.bank_sensitivity == 4) & (st.srd == 2)]


# SIMULATION for a set of percentage RD. This is used along with A1_plots_montecarlo_sensitivity_interestrate
# srdvalues = np.arange(0.01, 0.01, 0.01)


srdvalues = [0.01] # Sigma RD. Percentage on revenues invested in RD
elvalues = [6] # [3, 6, 10, 20, 30, 100, 10000]
taxvalues = [0] # percentage of taxes

st = [{'el': [], 'tax': [], 'phi': [], 'credit_mode': [], 'srd': [], 'bank_sensitivity': [], 'r1': []}]
ls = 0
for el in elvalues:
    for tax in taxvalues:
        tax1 = tax * 100  # to save files
        for O_phi in [3]:  # Evolution of the productivity over time is fixed 0.1 for new entries
            for credit_mode in [1]:  # RD based on RD cost.
                for srd in srdvalues:  # RD, RESEARCH (OUR INTEREST)
                    srd_index = srd * 100  # to save files
                    for z in [1]:  # policy, interest cut, debt relief (IREF, SECTION 5.2)
                        alpha_r = z
                        for bank_sensitivity in [1]:  # policy, debt rescheduling (1-4) (IREF, SECTION 5.1)
                            print('bank sensityvity = ' + str(bank_sensitivity))
                            st[ls]['el'] = el
                            st[ls]['tax'] = tax1
                            st[ls]['phi'] = O_phi
                            st[ls]['credit_mode'] = credit_mode
                            st[ls]['srd'] = srd_index
                            st[ls]['bank_sensitivity'] = bank_sensitivity
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            # % CREATE NEW VARIABLES (COMPARED TO IREF) FOR EACH MONTECARLO
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            RD_M_montecarlo = []  # cost on research
                            firm_tax_M_montecarlo = []  # tax of firms
                            success_perct_M_montecarlo = []  # percentage of success
                            phi_M_montecarlo = []  # phi of the system
                            positive_firms_M_montecarlo = []  # firms with profits
                            P_M_montecarlo = []  # profits of the firms
                            P2_M_montecarlo = []  # profits of the firms
                            phi_failure_M_montecarlo = []  # still experimental
                            phi_survive_M_montecarlo = []  # still experimental
                            Rv_M_montecarlo = []  # detailed information of profits: revenue
                            PL_M_montecarlo = []  # detailed information of profits: past losses
                            OC_M_montecarlo = []  # detailed information of profits: opetarional cost
                            C_D_M_montecarlo = []  # checks nothing
                            surviverdata_M_montecarlo = []  # data of surviving firms
                            surviverdata_table = []  # data of surviving firms in a table
                            L_M_montecarlo = []  # loans, credit demand,
                            A_M_end_montecarlo = []
                            phi_M_end_montecarlo = []
                            pool_tax_M_montecarlo = []
                            M_ts_gamma_M = []
                            gamma_M_montecarlo = []
                            r_M_montecarlo = []
                            dK_M_montecarlo = []
                            sL_M_montecarlo = []
                            K_M_montecarlo = []
                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            gg_M_montecarlo = []
                            A_M_montecarlo = []
                            A_bank_M_montecarlo = []
                            Y_M_montecarlo = []
                            C_M_montecarlo = []
                            leverage_ratio_M_montecarlo = []
                            equity_ratio_M_montecarlo = []
                            n_failures_I_montecarlo = []
                            n_failures_II_montecarlo = []
                            n_failures_III_montecarlo = []
                            n_firms_shortaged_failed_by_equity_montecarlo = []
                            n_firms_shortaged_montecarlo = []
                            iCopertura_M_montecarlo = []
                            M_ts_gg_M = []
                            M_ts_Y_M = []
                            M_ts_A_M = []
                            M_ts_C_M = []
                            M_ts_A_bank_M = []
                            M_ts_leverage_ratio_M = []
                            M_ts_equity_ratio_M = []
                            M_ts_r_M = []
                            M_ts_BS = []
                            M_r_L_A = []
                            M_l_L_A = []
                            M_iCopertura = []
                            for n_m in range(n_montecarlo):
                                nn = 0
                                print('n montecarlo = ' + str(n_m))
                                np.random.seed(20579+n_m)
                                space_print1 = '%f\t' * n_montecarlo + '\n'
                                space_print2 = '%f\t' * (n_montecarlo + 2) + '\n'
                                space_print3 = '%f\t' * ((4 * n_montecarlo) + 2) + '\n'
                                # %% initialize variables
                                K_entry = 5
                                min_K = K_entry / 2
                                A_entry = 1
                                A_exit = 0
                                L_entry = 4
                                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                # % INITIALIZE NEW VARIABLES (COMPARED TO IREF)
                                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                phi = np.zeros((Nfirms, 2))
                                phi[:, 1] = phi_entry  # productivity
                                phi_entry_matrix = np.ones((Nfirms, 1)) * phi_entry  # not used in the end
                                RD = np.zeros((Nfirms, 2))
                                RD[:, 1] = 0  # cost on research
                                mu = np.zeros((Nfirms, 1))  # ratio RD/K for bernoulli
                                z_bernoulli = np.zeros((Nfirms, 1))  # bernoulli
                                success = np.zeros((Nfirms, 1))  # probability of success (yes or not)
                                firm_tax = np.zeros((Nfirms, 1))
                                phi_M = np.empty( Nfirms )   # _M saves data within a given montecarlo, for each time t
                                success_M = np.empty( Nfirms )
                                RD_M = np.empty( Nfirms )
                                mu_M = np.empty( Nfirms )
                                firm_tax_M = np.empty( Nfirms )
                                total_taxes_M = np.empty( 0 )
                                success_perct_M = np.empty( 0 )
                                positive_firms_M = np.empty( 0 )
                                P_M = np.empty( Nfirms )
                                P2_M = np.empty( Nfirms )
                                K_operative = np.zeros((Nfirms, 1))
                                subRD = np.zeros((Nfirms, nt))
                                subrevenue = np.zeros((Nfirms, nt))
                                phi_failure_M = np.empty( Nfirms )
                                phi_survive_M = np.empty( Nfirms )
                                Rv = np.zeros((Nfirms, 1))
                                Rv_M = np.empty( Nfirms )
                                PL = np.zeros((Nfirms, 1))
                                PL_M = np.empty( Nfirms )
                                OC = np.zeros((Nfirms, 1))
                                OC_M = np.empty( Nfirms )
                                C_D_M = np.empty( Nfirms )
                                survive = np.zeros((Nfirms, 1))
                                phiinicial = np.zeros((Nfirms, 1))
                                phifinal = np.zeros((Nfirms, 1))
                                surviverdata_M = []
                                surviverdata = []
                                surviverdata_table = []
                                pool_tax = 0
                                pool_tax_M = np.empty( Nfirms )
                                gamma = np.zeros((Nfirms, 2))
                                gamma_M = np.empty( Nfirms )
                                dK_M = np.empty( Nfirms )
                                sL_M = np.empty( Nfirms )
                                # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                initial_equity_ratio = A_entry / K_entry
                                K = np.zeros((Nfirms, 2))
                                K[:, 1] = K_entry
                                A = np.zeros((Nfirms, 2))
                                A[:, 1] = A_entry
                                L = np.zeros((Nfirms, 2))
                                L[:, 1] = L_entry
                                C = np.zeros((Nfirms, 1))
                                C2 = np.zeros((Nfirms, 1))
                                A_bank = np.zeros((1, 2))
                                A_bank[:, 1] = nu * Nfirms * np.unique(L[:, 1])
                                Y = np.zeros((Nfirms, 2))
                                B_equity = np.zeros((1, 2))
                                L_back_to_bank = np.zeros((1, 1))
                                P = np.zeros((Nfirms, 2))
                                P2 = np.zeros((Nfirms, 2))
                                dK = np.zeros((Nfirms, 2))
                                subP = np.zeros((Nfirms, nt))
                                P_remained = np.zeros((Nfirms, 2))
                                liquidity = np.zeros((Nfirms, 2))
                                I = np.zeros((Nfirms, 1))
                                F = np.zeros((Nfirms, 2))
                                FF = np.zeros((Nfirms, 2))
                                r = np.zeros((Nfirms, 2))
                                leverage_firm = np.zeros((Nfirms, 2))
                                leverage_firm[:, 1] = L[:, 1] / A[:, 1]
                                equity_ratio = np.zeros((Nfirms, 2))
                                equity_ratio[:, 1] = A[:, 1] / K[:, 1]
                                share_failure = np.zeros((T, 1))
                                n_failure = np.zeros((T, 1))
                                rel_size_failure = np.zeros((T, 1))
                                r_bar = np.zeros((T, 1))
                                num_firms = np.zeros((T, 1))
                                failureI = np.zeros((T, 1))
                                failureII = np.zeros((T, 1))
                                failureIII = np.zeros((T, 1))
                                n_firms_shortaged = np.zeros((T, 1))
                                n_firms_shortaged_failed_by_equity = np.zeros((T, 1))
                                r_mean = np.zeros((T, 1))
                                iCopertura = np.zeros((Nfirms, 1))
                                A_M = []
                                A_bank_M = []
                                Y_M = []
                                gg_M = []
                                gg1_M = []
                                C_M = []
                                r_M = []
                                F_M = []
                                FF_M = []
                                K_M = []
                                L_M = []
                                B_equity_M = []
                                equity_ratio_M = []
                                leverage_ratio_M = []
                                iCopertura_M = []
                                # %%
                                for t in range(T):  # total steps 1000=T
                                    if t > 1:
                                        #                 if mod(t, 500)==0
                                        #                     fprintf('%d\n', t)
                                        #                 end
                                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        # This variable is created to save (and clean for new t) the information
                                        # related to the firms since they entry until they fail.
                                        surviverdata = []
                                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        # %% stats death firms
                                        ind = np.where(F[:, 0] == 1)
                                        if len(ind) > 0:
                                            n_failure[t, 0] = len(ind)
                                            share_failure[t, 0] = n_failure[t, 0] / Nfirms
                                            rel_size_failure[t, 0] = np.sum(A[ind, 1]) / np.sum(A[:, 1])
                                        # %% flip flop procedure
                                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        # FLIP FLOP NEW VARIABLES (COMPARED TO IREF)
                                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        phi[:, 1] = phi[:, 0]
                                        phi[:, 0] = 0
                                        RD[:, 1] = RD[:, 0]
                                        RD[:, 0] = 0
                                        mu[:, 0] = 0
                                        z_bernoulli[:, 0] = 0
                                        success[:, 0] = 0
                                        firm_tax[:, 0] = 0
                                        subRD[:, :] = 0
                                        subrevenue[:, :] = 0
                                        Rv[:, 0] = 0
                                        PL[:, 0] = 0
                                        OC[:, 0] = 0
                                        gamma[:, 1] = gamma[:, 0]
                                        gamma[:, 0] = 0
                                        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        A[:, 1] = A[:, 0]
                                        A[:, 0] = 0
                                        P[:, 1] = P[:, 0]
                                        P[:, 0] = 0
                                        P2[:, 1] = P2[:, 0]
                                        P2[:, 0] = 0
                                        Y[:, 1] = Y[:, 0]
                                        Y[:, 0] = 0
                                        L[:, 1] = L[:, 0]
                                        L[:, 0] = 0
                                        B_equity[:, 1] = B_equity[:, 0]
                                        B_equity[:, 0] = 0
                                        K[:, 1] = K[:, 0]
                                        K[:, 0] = 0
                                        r[:, 1] = r[:, 0]
                                        r[:, 0] = 0
                                        F[:, 1] = F[:, 0]
                                        F[:, 0] = 0
                                        FF[:, 1] = FF[:, 0]
                                        FF[:, 0] = 0
                                        dK[:, 1] = dK[:, 0]
                                        dK[:, 0] = 0
                                        subP[:, :] = 0
                                        P_remained[:, 1] = P_remained[:, 0]
                                        P_remained[:, 0] = 0
                                        A_bank[0, 1] = A_bank[0, 0]
                                        A_bank[0, 0] = 0
                                        equity_ratio[:, 1] = equity_ratio[:, 0]
                                        equity_ratio[:, 0] = 0
                                        leverage_firm[:, 1] = leverage_firm[:, 0]
                                        leverage_firm[:, 0] = 0
                                        liquidity[:, 1] = liquidity[:, 0]
                                        liquidity[:, 0] = 0
                                        iCopertura = np.zeros((Nfirms, 1))
                                        # %% entry new firms
                                        n_entry = n_failure[t, 0]
                                        if n_entry > 0:
                                            if ans_mode == 0:
                                                A_entry = np.median(A[A[:, 1] > 0, 1]) / 1.25
                                                K_entry = A_entry / np.median(equity_ratio[A[:, 1] > 0, 1])
                                            elif ans_mode == 1:
                                                ind = F[:, 1] == 0
                                                a_mode = np.nanmedian(equity_ratio[ind, 1])
                                                K_mode = np.nanmedian(np.ceil(K[:, 1]))
                                                K_entry = K_mode
                                                A_entry = K_entry * a_mode
                                            elif ans_mode == 2:
                                                K_entry = 5
                                                A_entry = 1
                                            elif ans_mode == 3:
                                                A_entry = np.min(A[A[:, 1] > 0, 1])
                                                K_entry = np.min(K[K[:, 1] > 0, 1])
                                            elif ans_mode == 4:
                                                ind = np.where(F[:, 1] == 0)
                                                random_entry = np.ceil(
                                                    np.random.rand(n_failure[t, 0], 1) * len(ind))
                                                random_entry_ind = (ind[random_entry])
                                                A_entry = A[random_entry_ind, 1]
                                                a_mean = np.mean(equity_ratio[:, 1])
                                                K_entry = A_entry / a_mean
                                            L_entry = K_entry - A_entry
                                            ind = np.where(F[:, 1] == 1)
                                            A[ind, 1] = A_entry
                                            K[ind, 1] = K_entry
                                            L[ind, 1] = L_entry
                                            leverage_firm[ind, 1] = L_entry / A_entry
                                            equity_ratio[ind, 1] = A_entry / K_entry
                                            r[ind, 1] = 0
                                            dK[ind, 1] = 0
                                            Y[ind, 1] = 0
                                            P[ind, :] = 0
                                            P2[ind, :] = 0
                                            B_equity[ind, 1] = 0
                                            subP[ind, :] = 0
                                            P_remained[ind, :] = 0
                                            liquidity[ind, :] = 0
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            # % OPTIONS FOR THE PRODUCTIVITY (phi) OF NEW ENTRIES
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            # %%%%%%%%%%%%%%%%%%%% O1: MEAN OF THE SYSTEM
                                            if O_phi == 1:
                                                phi[ind, 1] = np.mean(phi[:, 1])
                                            # %%%%%%%%%%%%%%%%%%%% O2 : MEDIAN OF THE SYSTEM
                                            elif O_phi == 2:
                                                phi[ind, 1] = np.median(phi[:, 1])
                                            # %%%%%%%%%%%%%%%%%%%%% O3: FIXED AT 0.1
                                            elif O_phi == 3:
                                                phi[ind, 1] = phi_entry
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            # O4: ACCORDING TO A GIVEN PERCENTILE OF THE SYSTEM
                                            # d2_e=mean(phi(:, 2));
                                            # d1_e=phi_entry;
                                            elif O_phi == 4:
                                                d2_e = np.percentile(phi[:, 1], pd2)
                                                d1_e = np.percentile(phi[:, 1], pd1)
                                                rn_entry = d1_e + (d2_e - d1_e) * np.random.rand(Nfirms, 1)
                                                phi[ind, 1] = rn_entry[ind, 0]
                                            # O5: AROUND THE MEDIAN OF THE SYSTEM WITH ONE SD.
                                            elif O_phi == 5:
                                                d1_e = np.median(phi[:, 1]) - rstd * np.std(phi[:, 1])
                                                d2_e = np.median(phi[:, 1]) + rstd * np.std(phi[:, 1])
                                                if d1_e < 0.1:
                                                    d1_e = 0.1
                                                rn_entry = d1_e + (d2_e - d1_e) * np.random.rand(Nfirms, 1)
                                                phi[ind, 1] = rn_entry[ind, 0]
                                            # O6: MODE
                                            elif O_phi == 6:
                                                phi[ind, 1] = np.mode(phi[:, 1])
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            # NEW VARIABLES
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                            K_operative[ind, 0] = 0
                                            subRD[ind, :] = 0
                                            Rv[ind, :] = 0
                                            PL[ind, :] = 0
                                            OC[ind, :] = 0
                                            survive[ind, :] = 0
                                            phiinicial[ind, :] = 0
                                            phifinal[ind, :] = 0
                                            gamma[ind, 1] = 0
                                    A_exit = np.min(A[:, 1])
                                    # %%%%% t=0, we start here
                                    # %% bank credit supply
                                    totL = A_bank[0, 1] / nu
                                    a = A[:, 1] / np.sum(A[:, 1])
                                    k = K[:, 1] / np.sum(K[:, 1])
                                    sL = (totL * (1 - lambda_val) * a) + (totL * lambda_val * k)
                                    # %% equity ratio
                                    equity_ratio[:, 0] = A[:, 1] / K[:, 1]  # equity ratio
                                    if np.any(equity_ratio[:, 0] < 0):
                                        print('equity is negative')
                                    # %% interest rate
                                    r1 = 2 + A[:, 1]
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # MODIFIED FORMULA ACCORDING TO THE MODEL
                                    r2 = (2 * c * g * ((1 / (c * phi[:, 1])) + P[:, 1] + A[:, 1])) + (
                                                2 * c * g * sL)
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    r[:, 0] = r1 / r2
                                    r[:, 0] = beta * (L[:, 1] / A[:, 1])
                                    ind = np.where(P_remained[:, 1] < 0)
                                    if len(ind) > 0:
                                        r[ind, 0] = r[ind, 0] * (alpha_r)
                                    ind = np.where(r[:, 0] < bar)
                                    if len(ind) > 0:
                                        r[ind, 0] = bar
                                    ind = np.where(r[:, 0] > bar_max)
                                    if len(ind) > 0:
                                        r[ind, 0] = bar_max
                                    if np.any(r[:, 0] < 0):
                                        print('negative r')
                                        print(t)
                                        sys.exit(0)
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # GAMMA
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    gamma[:, 0] = (wage / ki) + g * r[:, 0]
                                    # %%% GAB, INCLUIR BARRIER???????????
                                    # %% desired capital
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # MODIFIED FORMULA ACCORDING TO THE MODEL
                                    dK1 = (( ((((1 - 1 / el) ** 2) * phi[:, 1] - (1 - 1 / el) * gamma[:, 0]))  * (1 - srd))
                                                     /
                                                   ( c * phi[:, 1] * gamma[:, 0]) )
                                    # dK1[:, 0] = ((((1-1/el)^2).*phi(:, 2)-((1-1/el).*gamma(:, 1))-(1-1/el).*srd.*phi(:, 2)).*(1-srd-tax+srd.*tax))./(c.*phi(:, 2).*gamma(:, 1));
                                    dK2 = (A[:, 1] / (2 * gamma[:, 0] * (1 - tax)))
                                    dK[:, 0] = dK1 + dK2
                                    #             dK1old[:, 1) = ((phi(:, 2)-(g.*r(:, 1))-srd.*phi(:, 2)).*(1-srd-tax+srd.*tax))./(c.*phi(:, 2).*g.*r(:, 1));
                                    #             dK2old[:, 1) = A(:, 2)./(2.*g.*r(:, 1).*(1-tax));
                                    #             dKold[:, 1) = dK1(:, 1)+ dK2(:, 1);
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    ind = np.where(dK[:, 0] < share_K * K[:, 1])
                                    if len(ind) > 0:
                                        dK[ind, 0] = share_K * K[ind, 1]
                                    ind = np.where(dK[:, 0] < 0)
                                    if len(ind) > 0:
                                        print('dK is negative')
                                        dK[ind, 0] = min_K
                                        print(t)
                                        # return
                                    # %% credit demand
                                    I[:, 0] = dK[:, 0] - K[:, 1]
                                    L[:, 0] = L[:, 1] + I[:, 0] - P[:, 1]
                                    if np.any(L[:, 0] < 0):
                                        # warning('N.B. negative liabilities')
                                        ind = np.where(L[:, 0] < 0)
                                        A[ind, 1] = A[ind, 1] + np.abs(L[ind, 0])
                                        L[ind, 0] = 0
                                    ind = np.where(A[:, 1] + L[:, 0] - dK[:, 0] > 0)
                                    if len(ind) > 0:
                                        A[ind, 1] = -L[ind, 0] + dK[ind, 0]
                                    # %%
                                    # %% firm leverage
                                    leverage_firm[:, 0] = L[:, 0] / A[:, 1]
                                    # M_l_L_A = [M_l_L_A; [mean(leverage_firm(:, 1)), sum(L(:, 1)), sum(A(:, 2))]];
                                    # %% capital
                                    ind, = np.where(sL >= L[:, 1])
                                    if len(ind) > 0:
                                        K[ind, 0] = dK[ind, 0]
                                    ind, = np.where(sL < L[:, 0])
                                    if len(ind) > 0:
                                        L[ind, 0] = sL
                                        K[ind, 0] = L[ind, 0] + A[ind, 1]
                                        K1 = None
                                        K2 = None
                                    ind = [i for i, val in enumerate(L[:, 0]) if val < 0]
                                    if ind!=([],):
                                        A[ind, 1] = A[ind, 1] + abs(L[ind, 0])
                                        L[ind, 0] = 0
                                        print('L is negative')
                                        print(ind)
                                        print(t)
                                    if any(K[:, 0] < 0):
                                        print('K is negative')
                                        print(t)
                                        sys.exit(0)
                                    if ans_cash == 1:
                                        C[:, 0] = share_cash * K[:, 0]
                                        K[:, 0] = (1 - share_cash) * K[:, 0]
                                        K_operative[:,0] = K[:, 0]
                                    r_bar[t, 0] = sum(r[:, 0] * L[:, 0]) / sum(L[:, 0])
                                    Y[:, 0] = phi[:, 1] * K[:, 0]
                                    SY = Y[:, 0] / nt
                                    for subperiods in range(1, nt+1):
                                        u = (umin + (umax * np.random.rand(Nfirms, 1)))[:,0]
                                        subP[:, subperiods-1] = u * (1/el + (1-1/el)*SY) - \
                                            ((gamma[:, 0] * K[:, 0]) / nt) - \
                                            srd * u * (1/el + (1-1/el)*SY) - \
                                            (abs(P_remained[:, 1])/nt)
                                        subRD[:, subperiods-1] = srd * u * (1/el + (1-1/el)*SY)
                                        subrevenue[:, subperiods-1] = u * (1/el + (1-1/el)*SY)
                                        ind = [i for i, val in enumerate(subP[:, subperiods-1]) if val < 0]
                                        liquidity[ind, 0] = liquidity[ind, 0] + 1
                                    P[:, 0] = np.sum(subP, axis=1)
                                    P2[:, 0] = np.sum(subP, axis=1)
                                    RD[:,0] = np.sum(subRD, axis=1)
                                    Rv[:,0] = np.sum(subrevenue, axis=1)
                                    OC[:,0] = gamma[:, 0] * K[:, 0]
                                    PL[:,0] = abs(P_remained[:, 1])
                                    if ans_cash == 1:
                                        C1 = C
                                        ind = [i for i, val in enumerate(P[:, 0]) if val < 0]
                                        ind2 = [i for i, val in enumerate(abs(P[ind, 0])) if val > C[ind, 0]]
                                        if ind2:
                                            for i_ind2 in ind2:
                                                P[ind[i_ind2], 0] = P[ind[i_ind2], 0] + C[ind[i_ind2], 0]
                                                C[ind[i_ind2], 0] = 0
                                        ind2 = [i for i, val in enumerate(abs(P[ind, 0])) if val <= C[ind, 0]]
                                        if ind2:
                                            for i_ind2 in ind2:
                                                C[ind[i_ind2], 0] = C[ind[i_ind2], 0] + P[ind[i_ind2], 0]
                                                P[ind[i_ind2], 0] = 0
                                        C_D = C
                                        K[:, 0] = K[:, 0] + C[:, 0]
                                        C2 = (C - C1)/C
                                        C[:, 0] = 0
                                    ind_first_year = [i for i, val in enumerate(P_remained[:, 1]) if val == 0]
                                    ind_first_year_tax = [i for i, val in enumerate(P_remained[:, 1]) if val == 0]
                                    ind = [i for i, val in enumerate(P[ind_first_year, 0]) if val >= 0]
                                    for i_ind in ind:
                                        P_remained[ind_first_year[i_ind], 0] = 0
                                        A[ind_first_year[i_ind], 0] = A[ind_first_year[i_ind], 1] + P[ind_first_year[i_ind], 0]
                                    ind = [i for i, val in enumerate(P[ind_first_year, 0]) if val < 0]
                                    ind_tax = [i for i, val in enumerate(P[ind_first_year_tax, 0]) if val < 0]
                                    if credit_mode == 1:
                                        avg_size = np.mean(RD[:, 0])
                                        ind_small= [i for i, val in enumerate(RD[ind], 0) if val[0] < avg_size]
                                        for i_ind in ind_small:
                                            P_remained[ind_first_year[i_ind], 0] = 0
                                            A[ind_first_year[ind_small], 0] = A[ind_first_year[ind[i_ind]], 1] + P[ind_first_year[ind[i_ind]], 0]
                                        ind_big = [i for i, val in enumerate(RD[ind], 0) if val >= avg_size]

                                        # avg_size = np.mean(RD[:, 0])
                                        # ind_small = [i for i, val in enumerate(RD[ind_first_year[ind], 1]) if
                                        #              val < avg_size]
                                        # P_remained[ind_first_year[ind[ind_small]], 0] = 0
                                        # A[ind_first_year[ind[ind_small]], 0] = A[ind_first_year[ind[ind_small]], 1] + P[
                                        #     ind_first_year[ind[ind_small]], 0]
                                        # ind_big = [i for i, val in enumerate(RD[ind_first_year[ind], 0]) if
                                        #            val >= avg_size]
                                    elif credit_mode == 2:
                                        avg_size = np.mean(phi[:, 1])
                                        ind_small = [i for i, val in enumerate(phi[ind_first_year[ind], 1]) if val < avg_size]
                                        P_remained[ind_first_year[ind[ind_small]], 0] = 0
                                        A[ind_first_year[ind[ind_small]], 0] = A[ind_first_year[ind[ind_small]], 1] + P[ind_first_year[ind[ind_small]], 0]
                                        ind_big = [i for i, val in enumerate(phi[ind_first_year[ind], 1]) if val >= avg_size]

                                        # avg_size = np.mean(phi[:, 1])
                                        # ind_small = [i for i, val in enumerate(phi[ind_first_year[ind], 1]) if
                                        #              val < avg_size]
                                        # P_remained[ind_first_year[ind[ind_small]], 0] = 0
                                        # A[ind_first_year[ind[ind_small]], 0] = A[ind_first_year[ind[ind_small]], 1] + P[
                                        #     ind_first_year[ind[ind_small]], 0]
                                        # ind_big = [i for i, val in enumerate(phi[ind_first_year[ind], 1]) if
                                        #            val >= avg_size]
                                    if ind_big:
                                        if ans_iCopertura == 1:
                                            ind_neg = [i for i, val in enumerate(P[ind_first_year[ind], 0]) if val < 0]
                                            iCopertura[ind_first_year, 0] = P[ind_first_year]/min(P[ind_first_year[ind]])
                                            prct = np.percentile(iCopertura, 75)
                                            ind_prct = [i for i, val in enumerate(iCopertura[ind[ind_big], 0]) if val >= prct]
                                            if ind_prct:
                                                nn = nn + len(ind_prct)
                                                A[ind_first_year[ind[ind_big[ind_prct]]], 0] = A[ind_first_year[ind[ind_big[ind_prct]]], 1]
                                                P_remained[ind_first_year[ind[ind_big[ind_prct]]], 0] = P[ind_first_year[ind[ind_big[ind_prct]]], 0]
                                                P[ind_first_year[ind[ind_big[ind_prct]]], 0] = 0
                                            ind_prct = [i for i, val in enumerate(iCopertura[ind[ind_big], 0]) if val < prct]
                                            if ind_prct:
                                                A[ind_first_year[ind[ind_big[ind_prct]]], 0] = A[ind_first_year[ind[ind_big[ind_prct]]], 1] + P[ind_first_year[ind[ind_big[ind_prct]]], 0]
                                                P_remained[ind_first_year[ind[ind_big[ind_prct]]], 0] = 0
                                        else:
                                            A[ind_first_year[ind[ind_big]], 0] = A[ind_first_year[ind[ind_big]], 1]
                                            P_remained[ind_first_year[ind[ind_big]], 0] = P[ind_first_year[ind[ind_big]], 0]
                                            P[ind_first_year[ind[ind_big]], 0] = 0
                                    ind_second_year = [i for i, val in enumerate(P_remained[:, 1]) if val != 0]
                                    n_firms_shortaged[t, 0] = len(ind_second_year)
                                    firm_failed_liquidity = []
                                    if ind_second_year:
                                        A[ind_second_year, 0] = A[ind_second_year, 1] + P[ind_second_year, 0]
                                        P_remained[ind_second_year, 0] = 0
                                        ind = [i for i, val in enumerate(liquidity[ind_second_year, 0]) if val >= bank_sensitivity]
                                        if ind:
                                            firm_failed_liquidity = ind_second_year[ind]
                                            L_back_to_bank[0, 0] = sum(K[firm_failed_liquidity, 0]) + sum(A[firm_failed_liquidity, 0]) - sum(L[firm_failed_liquidity, 0])
                                    ind_equity = [i for i, val in enumerate(A[:, 0]) if val < A_exit]
                                    B_equity[0, 0] = sum(A[ind_equity, 0])
                                    failureI[t, 0] = len(ind_equity)
                                    F[ind_equity, 0] = 1
                                    FF[ind_equity, 0] = 1
                                    ind = [i for i, val in enumerate(liquidity[ind_second_year, 0]) if val >= nt]
                                    if ind:
                                        firm_failed_liquidity = ind_second_year[ind]
                                    failureII[t, 0] = len(ind)
                                    if len(ind_second_year)>0:
                                        # ++ojo++ division by zero
                                        failureIII[t, 0] = failureII[t, 0]/len(ind_second_year)
                                    else:
                                        failureIII[t, 0] = failureII[t, 0]/len(ind_second_year)
                                    F[ind, 0] = 1
                                    FF[ind, 0] = 2
                                    n_firms_shortaged_failed_by_equity[t, 0] = len(firm_failed_liquidity) - len(ind)
                                    phi_failure = phi[:, 1] * F[:, 0]
                                    noF = np.logical_not(F)
                                    phi_survive = phi[:, 1] * noF[:, 0]
                                    phi_failure[phi_failure==0] = np.nan
                                    phi_survive[phi_survive==0] = np.nan

                                    # SURVIVER
                                    ind_survive = np.where(F[:, 0] == 0)[0]  # sobrevive
                                    survive[ind_survive, 0] += 1  # numero de periodos t que sobrevive
                                    ind_phiinicial = np.where(survive[:, 0] == 1)[0]  # quien sobrevive
                                    phiinicial[ind_phiinicial, 0] = phi[
                                        ind_phiinicial, 1]  # guardar phi inicial si es el primer año de la empresa
                                    ind_nosurvive = np.where(F[:, 0] == 1)[0]  # quiebra
                                    phifinal[ind_nosurvive, 0] = phi[
                                        ind_nosurvive, 1]  # si quiebra guardo su ultimo phi

                                    surviverdata = ind_nosurvive  # record años sobrevividos
                                    surviverdata = np.c_[ surviverdata, (phifinal[ind_nosurvive, 0] - phiinicial[ind_nosurvive, 0]) / \
                                                          phiinicial[ind_nosurvive, 0] ]
                                    surviverdata[np.isinf(surviverdata)] = 0
                                    # if t > 1
                                    # surviverdata[:,2] = (phi_M[ind_nosurvive,t-1] - phi_M[ind_nosurvive,t-surviverdata[:,0]]) / phi_M[ind_nosurvive,t-surviverdata[:,0]]
                                    # end
                                    surviverdata = np.c_[ surviverdata, K[ind_nosurvive, 0]]
                                    surviverdata = np.c_[ surviverdata, A[ind_nosurvive, 0]]
                                    surviverdata = np.c_[ surviverdata, leverage_firm[ind_nosurvive, 0]]
                                    surviverdata = np.c_[ surviverdata, np.full((len(ind_nosurvive)), t )]
                                    surviverdata = np.c_[ surviverdata, ind_nosurvive]
                                    surviverdata = np.c_[ surviverdata, np.full((len(ind_nosurvive)), n_m )]
                                    surviverdata = np.c_[ surviverdata, phifinal[ind_nosurvive, 0]]

                                    # bank update
                                    D = np.sum(L[:, 0]) - A_bank[0, 1]
                                    if np.any(D < 0):
                                        D = 0
                                    P_bank = np.sum(r[:, 0] * L[:, 0]) - (
                                                bar * (((1 - omega) * D) + A_bank[0, 1]))
                                    A_bank[0, 0] = A_bank[0, 1] + P_bank + B_equity[0, 0] + L_back_to_bank[0, 0]
                                    if A_bank[0, 0] < 0:
                                        print('A_bank is negative')
                                        print(t)
                                        sys.exit(0)

                                    # interest rate
                                    r_mean[t, 0] = np.sum(r[:, 0] * L[:, 0]) / np.sum(L[:, 0])

                                    # firm leverage, NOPE
                                    # leverage_firm[:,0] = L[:,0] / A[:,0]
                                    # M_l_L_A = [M_l_L_A; [np.mean(leverage_firm[:,0]), np.sum(L[:,0]), np.sum(A[:,1])]]

                                    # R&D PROCEDURE - Update phi - Bernoulli







                                    mu[:, 0] = RD[:, 0] / K_operative[:, 0]
                                    z_bernoulli[:, 0] = 1 - np.exp(-bb * mu[:, 0])
                                    success[:, 0] = np.random.binomial(1, z_bernoulli[:, 0])
                                    success_perct = np.sum(success[:, 0]) / Nfirms
                                    ind_first_year_pf = [i for i, val in enumerate(P_remained[:, 1]) if val == 0]
                                    ind_pf = [i for i, val in enumerate(P[ind_first_year_pf, 0]) if val > 0]
                                    positive_firms = len(ind_pf) / Nfirms
                                    rn_uni = d1 + (d2 - d1) * np.random.rand(Nfirms, 1)
                                    phi[:, 1] = phi[:, 1] * (1 + success[:, 0] * rn_uni[:, 0])
                                    check_ddd = np.column_stack((RD[:,0], mu, z_bernoulli, success, phi[:,1]))
                                    total_taxes = 0  # Cuando analices taxes: quitar esta linea y uncomment el resto
                                    if ans_record == 1:
                                        phi_M = np.c_[ phi_M, phi[:, 1] ]
                                        RD_M = np.c_[ RD_M, RD[:, 0] ]
                                        mu_M = np.c_[ mu_M, mu[:, 0] ]
                                        success_M = np.c_[ success_M, success[:, 0] ]
                                        firm_tax_M = np.c_[ firm_tax_M, firm_tax[:, 0] ]
                                        total_taxes_M = np.append( total_taxes_M, total_taxes)
                                        success_perct_M = np.append( success_perct_M, success_perct)
                                        positive_firms_M = np.append( positive_firms_M, positive_firms )
                                        # phi_M = np.column_stack((phi_M, phi[:, 1]))
                                        # RD_M = np.column_stack((RD_M, RD[:, 0]))
                                        # mu_M = np.column_stack((mu_M, mu[:, 0]))
                                        # success_M = np.column_stack((success_M, success[:, 0]))
                                        # firm_tax_M = np.column_stack((firm_tax_M, firm_tax[:, 0]))
                                        # total_taxes_M = np.column_stack((total_taxes_M, total_taxes))
                                        # success_perct_M = np.column_stack((success_perct_M, success_perct))
                                        # positive_firms_M = np.column_stack((positive_firms_M, positive_firms))
                                        # P_M = np.column_stack((P_M, P[:, 0]))
                                        # P2_M = np.column_stack((P2_M, P2[:, 0]))
                                        # phi_failure_M = np.column_stack((phi_failure_M, phi_failure[:, 0]))
                                        # phi_survive_M = np.column_stack((phi_survive_M, phi_survive[:, 0]))
                                        # Rv_M = np.column_stack((Rv_M, Rv[:, 0]))
                                        # PL_M = np.column_stack((PL_M, PL[:, 0]))
                                        # OC_M = np.column_stack((OC_M, OC[:, 0]))
                                        # C_D_M = np.column_stack((C_D_M, C_D))
                                        # surviverdata_M = np.vstack((surviverdata_M, surviverdata))
                                        P_M = np.c_[ P_M, P[:,0]]
                                        P2_M = np.c_[ P2_M, P2[:,0] ]
                                        phi_failure_M = np.c_[ phi_failure_M,phi_failure]
                                        phi_survive_M = np.c_[phi_survive_M,  phi_survive]
                                        Rv_M = np.c_[Rv_M,Rv[:,0]]
                                        PL_M = np.c_[PL_M,PL[:,0]]
                                        OC_M = np.c_[OC_M,OC[:,0]]
                                        C_D_M = np.c_[C_D_M,C_D]
                                        surviverdata_M.append(surviverdata)
                                        if T == 1000:
                                            surviverdata = pd.DataFrame(
                                                {'Periodssurvived': [], 'gr_phi': [], 'K': [], 'A': [], 'Lv': [],
                                                 't_death': [], 'firm_death': [], 'n_m': [], 'phi': []})
                                            # dataset = pd.DataFrame({'Column1': [], 'Column2': []})
                                            # surviverdata_table = pd.DataFrame(surviverdata_M,
                                            #                                   index=['Periodssurvived','gr_phi','K',
                                            #                                            'A', 'Lv', 't_death',
                                            #                                            'firm_death', 'n_m', 'phi'])
                                        np.append(pool_tax_M,pool_tax)
                                        np.append(gamma_M,gamma[:, 0])
                                        np.append(dK_M,dK[:, 0])
                                        np.append(sL_M,sL)
                                        np.append(C_M,C2[:, 0])
                                        np.append(A_M,A[:, 0])
                                        np.append(A_bank_M,A_bank[:, 0])
                                        np.append(Y_M,Y[:, 0])
                                        ind = np.where(F[:, 1] == 0)[0]
                                        gg = np.sum(P[:, 0]) / np.sum(A[:, 1])
                                        gg_M.append(gg)
                                        gg1 = P[:, 0] / A[:, 1]
                                        gg1_M.append(gg1)
                                        r_M.append(r[:, 0])
                                        F_M.append(F[:, 0])
                                        FF_M.append(FF[:, 0])
                                        B_equity_M.append(B_equity)
                                        equity_ratio_M.append(equity_ratio[:, 0])
                                        leverage_ratio_M.append(leverage_firm[:, 0])
                                        K_M.append(K[:, 0])
                                        L_M.append(L[:, 0])
                                        iCopertura_M.append(iCopertura)
                                    if n_m == 1:
                                        time_vec = []
                                        firm_vec = []
                                        for J in range(T):
                                            time_vec.extend([J] * Nfirms)
                                            firm_vec.extend(list(range(1, Nfirms + 1)))
                                        M_ts_gg_M = np.column_stack([(np.arange(1, T + 1)).reshape(-1, 1), np.ones((T, 1)), np.reshape(gg_M, (1 * 1000, 1))])
                                        M_ts_Y_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(Y_M, (Nfirms * 1000, 1))])
                                        M_ts_A_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(A_M, (Nfirms * 1000, 1))])
                                        M_ts_C_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(C_M, (Nfirms * 1000, 1))])
                                        M_ts_A_bank_M = np.column_stack([(np.arange(1, T + 1)).reshape(-1, 1), np.ones((T, 1)), np.reshape(A_bank_M, (1 * 1000, 1))])
                                        M_ts_leverage_ratio_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(leverage_ratio_M, (Nfirms * 1000, 1))])
                                        M_ts_equity_ratio_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(equity_ratio_M, (Nfirms * 1000, 1))])
                                        M_ts_r_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(r_M, (Nfirms * 1000, 1))])
                                        M_ts_r2_M = np.column_stack([(np.arange(1, T + 1)).reshape(-1, 1), np.ones((T, 1)), r_mean])
                                        M_ts_BS = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(K_M, (Nfirms * 1000, 1)), np.reshape(A_M, (Nfirms * 1000, 1)), np.reshape(L_M, (Nfirms * 1000, 1)), np.reshape(FF_M, (Nfirms * 1000, 1))])
                                        M_iCopertura_M = np.column_stack([np.array(time_vec).reshape(-1, 1), np.array(firm_vec).reshape(-1, 1), np.reshape(iCopertura_M, (Nfirms * 1000, 1))])
                                    else:
                                        M_ts_gg_M = np.column_stack([M_ts_gg_M, np.reshape(gg_M, (1 * 1000, 1))])
                                        M_ts_Y_M = np.column_stack([M_ts_Y_M, np.reshape(Y_M, (Nfirms * 1000, 1))])
                                        M_ts_A_M = np.column_stack([M_ts_A_M, np.reshape(A_M, (Nfirms * 1000, 1))])
                                        M_ts_C_M = np.column_stack([M_ts_C_M, np.reshape(C_M, (Nfirms * 1000, 1))])
                                        M_ts_A_bank_M = np.column_stack([M_ts_A_bank_M, np.reshape(A_bank_M, (1 * 1000, 1))])
                                        M_ts_leverage_ratio_M = np.column_stack([M_ts_leverage_ratio_M, np.reshape(leverage_ratio_M, (Nfirms * 1000, 1))])
                                        M_ts_equity_ratio_M = np.column_stack([M_ts_equity_ratio_M, np.reshape(equity_ratio_M, (Nfirms * 1000, 1))])
                                        M_ts_r_M = np.column_stack([M_ts_r_M, np.reshape(r_M, (Nfirms * 1000, 1))])
                                        M_ts_r2_M = np.column_stack([M_ts_r2_M, r_mean])
                                        M_ts_BS = np.column_stack([M_ts_BS, np.reshape(K_M, (Nfirms * 1000, 1)), np.reshape(A_M, (Nfirms * 1000, 1)), np.reshape(L_M, (Nfirms * 1000, 1)), np.reshape(FF_M, (Nfirms * 1000, 1))])
                                        M_iCopertura_M = np.column_stack([M_iCopertura_M, np.reshape(iCopertura_M, (Nfirms * 1000, 1))])
                                    nn
                                if ans_write_gab == 1:
                                    if ans_test_r == 1:
                                        directory2 = 'r' + str(100 - (alpha_r * 100)) + '_'
                                    else:
                                        directory2 = ''
                                    file = directory_gab + directory2 + 'firm_growth_rate_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_gg_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_Y_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_Y_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_C_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_C_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_A_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_A_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'bank_A_bank_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_A_bank_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'iCopertura_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_iCopertura_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_leverage_ratio_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_leverage_ratio_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_equity_ratio_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_equity_ratio_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_interest_rate_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_r_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_interest_rate2_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_r2_M, fmt=space_print2)
                                    file = directory_gab + directory2 + 'firm_balance_sheet_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, M_ts_BS, fmt=space_print3)
                                    file = directory_gab + directory2 + 'avg_growth_rate_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, gg_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_A_bank_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, A_bank_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'avg_iCopertura_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, iCopertura_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_A_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, A_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_Y_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, Y_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_C_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, C_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'avg_leverage_ratio_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, leverage_ratio_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'avg_equity_ratio_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, equity_ratio_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'n_failures_equity_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, n_failures_I_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'n_failures_liquidity_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, n_failures_II_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'n_failures_liquidity_share_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, n_failures_III_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'n_firms_shortaged_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, n_firms_shortaged_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'n_firms_shortaged_failed_by_equity_share_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, n_firms_shortaged_failed_by_equity_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_S_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, success_perct_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_phi_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, phi_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'aggr_pf_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, positive_firms_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'loan_model_sensytivity_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, L_M_montecarlo, fmt=space_print1)
                                    file = directory_gab + directory2 + 'A_M_end_' + str(O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(el) + '_el_' + str(tax1) + '_tax.txt'
                                    np.savetxt(file, A_M_end_montecarlo, fmt=space_print1)

                                    file = directory_gab + directory2 + 'pool_tax_M_' + str(O_phi) + '_O_phi_' + str(
                                        credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % pool_tax_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'firm_gamma_rate_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print2 % M_ts_gamma_M)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_gamma_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % gamma_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_r_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % r_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_P_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % P_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_P2_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % P2_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_r_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % r_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_P_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % P_M_montecarlo)
                                    fid.close()

                                    file = directory_gab + directory2 + 'aggr_P2_model_sensytivity_' + str(
                                        O_phi) + '_O_phi_' + str(credit_mode) + '_creditmode_' + str(
                                        bank_sensitivity) + '_interestrate_montecarlo_' + str(srd_index) + '_RD_' + str(
                                        el) + '_el_' + str(tax1) + '_tax.txt'
                                    fid = open(file, 'w')
                                    fid.write(space_print1 % P2_M_montecarlo)
                                    fid.close()






