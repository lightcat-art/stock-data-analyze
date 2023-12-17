-- django migration 전에 실행필요.
alter table stocksimul_infoupdatestatus modify table_type varchar(2);
update stocksimul_infoupdatestatus set table_type='EP' where table_type='P';
update stocksimul_infoupdatestatus set table_type='NP' where table_type='N';
update stocksimul_infoupdatestatus set table_type='FI' where table_type='I';
update stocksimul_infoupdatestatus set table_type='FH' where table_type='H';