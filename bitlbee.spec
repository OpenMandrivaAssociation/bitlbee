%define	name	bitlbee
%define	version	1.1dev
%define	rel	1
%define release %mkrel %{rel}
%define	Summary	IRC proxy to connect to ICQ, AOL, MSN and Jabber
%define	bitlbid	_bitlbee

# NOTE TO BACKPORTERS: You will need to remove ccp or include ccp in your
#			rpm repository

Summary:	%{Summary}
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Networking/Chat
URL:		http://bitlbee.org/
Source0:	http://get.bitlbee.org/src/%{name}-%{version}.tar.bz2
#Patch0:		http://get.bitlbee.org/patches/%{name}-%{version}-msn6.akke.diff.bz2
Buildrequires:	glib2-devel libsoup-devel >= 1.99.23
Requires(post):	ccp
Requires(pre):	rpm-helper
Requires:	xinetd

%description
%{name} is a proxy which accepts connections from any irc-client
and allows you to communicate using following instant messaging
protocols.

 - ICQ
 - AIM
 - MSN
 - YIM
 - Jabber (including Google talk)

%prep
%setup -q
#%patch0 -p0 -b .msn6
# Use the nick "bitlbee" instead of "root"
%{__sed} -i 's/ROOT_NICK "root"/ROOT_NICK "bitlbee"/' bitlbee.h

%build
perl -pi -e "s#CFLAGS=-O3#CFLAGS=$RPM_OPT_FLAGS -O3#g" configure
./configure	--prefix=%{_prefix} \
		--etcdir=%{_sysconfdir}/%{name} \
		--libdir=%{_libdir}/%{name}

%make

%install
%{__rm} -rf %{buildroot}
%{makeinstall_std} install-etc


%{__install} -d   %{buildroot}%{_var}/lib/%{name}
%{__install} -d   %{buildroot}%{_sysconfdir}/xinetd.d/
%{__cat} << EOF > %{buildroot}%{_sysconfdir}/xinetd.d/%{name}
# default: on
# description: bitlbee IRC2IM-proxy.
service ircd
{
	disable			= no
	socket_type		= stream
	protocol		= tcp
	wait			= no
	user			= %{bitlbid}
	server			= %{_sbindir}/%{name}
	log_on_success		+= DURATION USERID HOST
	log_on_failure		+= USERID HOST ATTEMPT
	nice			= 10
	bind			= 127.0.0.1
}
EOF


%pre
%_pre_useradd %{bitlbid} %{_var}/%{name} /bin/true
# in post it is harder to know if the new empty dir already exists
if [ $1 = 2 -a -d "%{_var}/%{name}" -a ! -d "%{_var}/lib/%{name}" ]; then
   echo -n " NOTE: new location of bitlbee users data: "
   mv -v "%{_var}/%{name}" "%{_var}/lib/%{name}"
fi

%post
ccp --delete --ifexists --set NoOprhans --oldfile %{_sysconfdir}/%{name}/%{name}.conf --newfile %{_sysconfdir}/%{name}/%{name}.conf.rpmnew
service xinetd condrestart
if ! pidof xinetd >/dev/null 2>/dev/null; then
   echo "Use the following command to start %{name}: /sbin/service xinetd start"
fi

%postun
%_postun_userdel %{bitlbid}
service xinetd condrestart

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(0750,root,%{bitlbid},0755)
%{_sbindir}/%{name}
%defattr(0644,root,root,0755)
%doc doc/AUTHORS doc/README doc/FAQ
%doc doc/CHANGES doc/CREDITS
%doc doc/user-guide/

%{_datadir}/%{name}/help.txt
%dir %{_datadir}/%{name}/
%{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/%{name}/motd.txt
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/xinetd.d/%{name}

%defattr(0600,%{bitlbid},%{bitlbid},0700)
%{_var}/lib/%{name}


