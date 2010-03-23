%define	name	bitlbee
%define	version	1.2.5
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
License:	GPLv2+
Group:		Networking/Chat
URL:		http://bitlbee.org/
Source0:	http://get.bitlbee.org/src/%{name}-%{version}.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Buildrequires:	glib2-devel libsoup-devel >= 1.99.23
Requires(post):	ccp
Requires(pre):	rpm-helper
Requires:	xinetd

# (misc) 11/2009 : seen this message when build on x86_64
#* Linking bitlbee
# /usr/bin/ld: i386 architecture of input file `/usr/lib/libresolv.a(res_data.o)' is incompatible with i386:x86-64 output
BuildConflicts: glibc-static-devel 

%description
%{name} is a proxy which accepts connections from any irc-client
and allows you to communicate using following instant messaging
protocols:

 - ICQ
 - AIM
 - MSN
 - YIM
 - Jabber (including Google talk)

%prep
%setup -q
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
