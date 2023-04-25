# Define macros
%define leapp_datadir %{_datadir}/leapp-repository
%define repositorydir %{leapp_datadir}/repositories
%define custom_repositorydir %{leapp_datadir}/custom-repositories
%define supplementsdir_name system_upgrade_supplements
%define supplementsdir %{custom_repositorydir}/%{supplementsdir_name}

# Define RPM Preamble
Name:           leapp-upgrade-el%{rhel}toel%{nextrhel}-supplements
Version:        1.0.0
Release:        1%{?dist}
Summary:        Custom actors for the Leapp project

License:        MIT
URL:            https://github.com/oamg/%{pkgname}
Source0:        %{pkgname}-%{version}.tar.gz

BuildArch:      noarch

%if 0%{?rhel} == 7
### RHEL 7 ###
BuildRequires:  python-devel

Requires:       leapp
Requires:       python2-leapp
# Dependency on leapp-repository
Requires:       leapp-upgrade-el7toel8
%endif

%if 0%{?rhel} == 8
### RHEL 8 ###
BuildRequires:  python3-devel

Requires:       leapp
Requires:       python3-leapp
# Dependency on leapp-repository
Requires:       leapp-upgrade-el8toel9
%endif

%description
Custom leapp actors for the in-place upgrade to the next major version
of the Red Hat Enterprise Linux system.

%prep
%autosetup -n %{pkgname}-%{version}

%install
install -m 0755 -d %{buildroot}%{custom_repositorydir}
install -m 0755 -d %{buildroot}%{repositorydir}
install -m 0755 -d %{buildroot}%{supplementsdir}
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/repos.d/
cp -r repos/%{supplementsdir_name}/* %{buildroot}%{supplementsdir}

# Remove irrelevant repositories - We don't want to ship them for the particular RHEL version
%if 0%{?rhel} == 7
rm -rf %{buildroot}%{supplementsdir}/el8toel9
%endif
%if 0%{?rhel} == 8
rm -rf %{buildroot}%{supplementsdir}/el7toel8
%endif

# Remove empty directories
find %{buildroot}%{supplementsdir}/ -type d -depth -empty -delete

# Remove actors not found in actors_to_install list
find %{buildroot}%{supplementsdir}/ -name actor.py -exec dirname {} \;  > tmp_actor_paths
while read -r actor_path; do
  actor_name=$(basename "$actor_path")
  # Check if actors is in actors_to_install list, if not: remove it
  echo "%{actors_to_install}" | grep -qw "${actor_name}" || rm -rf "$actor_path"
done < tmp_actor_paths
rm -f tmp_actor_paths

# Remove component/unit tests
rm -rf `find %{buildroot}%{supplementsdir} -name "tests" -type d`
find %{buildroot}%{repositorydir} -name "Makefile" -delete

# Create symlink to the supplements repository
ln -s %{supplementsdir} %{buildroot}%{_sysconfdir}/leapp/repos.d/%{supplementsdir_name}

# === Compile Python files ===
# __python2 could be problematic on systems with Python3 only, but we have
# no choice as __python became error on F33+:
# - https://fedoraproject.org/wiki/Changes/PythonMacroError
%if 0%{?rhel} == 7
%py_byte_compile %{__python2} %{buildroot}%{repositorydir}/*
%endif
%if 0%{?rhel} == 8
%py_byte_compile %{__python3} %{buildroot}%{repositorydir}/*
%endif

%files
%{supplementsdir}/*
%{_sysconfdir}/leapp/repos.d/%{supplementsdir_name}

%changelog
* Wed May 10 2023 Marek Filip <mafilip@redhat.com>
- First iteration of the packaging spec file
- Allow to install actors based on actors_to_install list
