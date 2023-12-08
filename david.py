import numpy as np

st = {'el': [], 'tax': [], 'phi': [], 'credit_mode': [], 'srd': [], 'bank_sensitivity': [], 'r1': []}
ls = 1
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
                                np.random.seed(s[n_m])
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
                                phi_M = []  # _M saves data within a given montecarlo, for each time t
                                success_M = []
                                RD_M = []
                                mu_M = []
                                firm_tax_M = []
                                total_taxes_M = []
                                success_perct_M = []
                                positive_firms_M = []
                                P_M = []
                                P2_M = []
                                K_operative = np.zeros((Nfirms, 1))
                                subRD = np.zeros((Nfirms, nt))
                                subrevenue = np.zeros((Nfirms, nt))
                                phi_failure_M = []
                                phi_survive_M = []
                                Rv = np.zeros((Nfirms, 1))
                                Rv_M = []
                                PL = np.zeros((Nfirms, 1))
                                PL_M = []
                                OC = np.zeros((Nfirms, 1))
                                OC_M = []
                                C_D_M = []
                                survive = np.zeros((Nfirms, 1))
                                phiinicial = np.zeros((Nfirms, 1))
                                phifinal = np.zeros((Nfirms, 1))
                                surviverdata_M = []
                                surviverdata = []
                                surviverdata_table = []
                                pool_tax = 0
                                pool_tax_M = []
                                gamma = np.zeros((Nfirms, 2))
                                gamma_M = []
                                dK_M = []
                                sL_M = []
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
                                equity_ratio = np.zeros((Nfirms, 1))
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
                                            # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                        end
                                    A_exit = np.min(A[:, 1])
                                    # %%%%% t=0, we start here
                                    # %% bank credit supply
                                    totL = A_bank[0, 1] / nu
                                    a = A[:, 1] / np.sum(A[:, 1])
                                    k = K[:, 1] / np.sum(K[:, 1])
                                    sL = (totL * (1 - lambda) * a) + (totL * (lambda) * k)
                                    # %% equity ratio
                                    equity_ratio[:, 0] = A[:, 1] / K[:, 1]  # equity ratio
                                    if np.any(equity_ratio[:, 0] < 0):
                                        print('equity is negative')
                                    # %% interest rate
                                    r1 = 2 + A[:, 1]
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # MODIFIED FORMULA ACCORDING TO THE MODEL
                                    r2 = (2 * c * g * ((1 / (c * phi[:, 1])) + P[:, 1] + A[:, 1])) + (
                                                2 * c * g * sL[:, 0])
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
                                        return
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # GAMMA
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    gamma[:, 0] = (wage / ki) + g * r[:, 0]
                                    # %%% GAB, INCLUIR BARRIER???????????
                                    # %% desired capital
                                    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                    # MODIFIED FORMULA ACCORDING TO THE MODEL
                                    dK1[:, 0] = ((((1 - 1 / el) ** 2) * phi[:, 1] - (
                                                (1 - 1 / el) * gamma[:, 0])) * (1 - srd)) / (
                                                               c * phi[:, 1] * gamma[:, 0])
                                    # dK1[:, 0] = ((((1-1/el)^2).*phi(:, 2)-((1-1/el).*gamma(:, 1))-(1-1/el).*srd.*phi(:, 2)).*(1-srd-tax+srd.*tax))./(c.*phi(:, 2).*gamma(:, 1));
                                    dK2[:, 0] = A[:, 1] / (2 * gamma[:, 0] * (1 - tax))
                                    dK[:, 0] = dK1[:, 0] + dK2[:, 0]
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
                                    ind = np.where(sL[:, 0] >= L[:, 0])
                                    if len(ind) > 0:
                                        K[ind, 0] = dK[ind, 0]
                                    ind = np.where(sL[:, 0] < L[:, 0])
                                    if len(ind) > 0:
                                        L[ind, 0] = s

