This python script automatically calls the qis-portal of University of Kaiserslautern. With the information stored in "cred.conf"
the given user is logged in and the grade-table (Master or Bachelor) is fetched. If there are some changes to a locally stored file "last_state.hist", the new grades are packed into a mail and sent to the e-mail address provided in cred.conf. The "last_state.hist" is then updated with 
the new grades. Hence a new request does not fetch the already fetched grades anymore.

IMPORTANT:
This only works within the local network of the University or via VPN.
I set up a respberry pi, that automatically connects to this VPN and then added a cronjob which periodically calls the qis-notify.py.
That way I am always notified, if there are new grades uploaded to my account.
