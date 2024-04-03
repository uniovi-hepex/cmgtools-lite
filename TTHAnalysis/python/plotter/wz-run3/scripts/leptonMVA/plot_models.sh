./plot_model.sh el_ttwPresel_nanoAODv12_2022EE_df           el_ttw_df_2022EE    el_ttw_df_noMVA_2022EE
./plot_model.sh el_ttwPresel_nanoAODv12_2022EE_df_useIso    el_ttw_df_useIso_2022EE    el_ttw_df_useIso_2022EE
./plot_model.sh el_ttwPresel_nanoAODv12_2022EE_df_useNoIso  el_ttw_df_useNoIso_2022EE    el_ttw_df_useNoIso_2022EE




python3 plot_ranking_fromxml.py el_df_useNoIso_2022EE el_ttw_df_useNoIso_2022EE
python3 plot_ranking_fromxml.py el_df_useIso_2022EE el_ttw_df_useIso_2022EE
python3 plot_ranking_fromxml.py el_df_noMVA_2022EE el_ttw_df_noMVA_2022EE

