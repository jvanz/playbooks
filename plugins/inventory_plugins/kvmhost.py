import libvirt

DOCUMENTATION = """
    name: kvmhost
    plugin_type: inventory
    author:
      - Jose Guilherme Vanz <jvanz@jvanz.com>
    short_description: Load KVM VMs
    description: Load KVM VMs
"""

from ansible.plugins.inventory import BaseInventoryPlugin


class InventoryModule(BaseInventoryPlugin):

    NAME = "kvmhost"  # used internally by Ansible, it should match the file name but not required

    def verify_file(self, path):
        return "kvmhost" in path


    def parse(self, inventory, loader, path, cache=True):
        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        kvmgroups = self.loader.load_from_file(path, cache=False)
        self.add_groups(kvmgroups, inventory)

        for kvmgroup in kvmgroups:
            for host in  inventory.get_groups_dict()[kvmgroup]:
                host_vars = inventory.get_host(host).get_vars()
                # connect to the qemu daemon
                if host_vars["ansible_connection"] == "local":
                    self.display.vvv(f"qemu URI: qemu:///system")
                    conn = libvirt.open("qemu:///system")
                else:
                    self.display.vvv(f"qemu URI: qemu+ssh://{host_vars['ansible_user']}@{host_vars['inventory_hostname']}/system")
                    conn = libvirt.open(f"qemu+ssh://{host_vars['ansible_user']}@{host_vars['inventory_hostname']}/system")

                for domain in conn.listAllDomains():
                    groups = self.get_group(domain, kvmgroups[kvmgroup])
                    self.display.vvv(str(groups))
                    for group in groups:
                        inventory.add_host(domain.name(), group)
                    inventory.set_variable(domain.name(), "hostmachine", host)
                    inventory.set_variable(domain.name(), "vm", True)
                    interfaces = domain.interfaceAddresses(0)
                    for interface in interfaces:
                        addrs = interfaces[interface].get("addrs", [])
                        if len(addrs) > 0:
                            inventory.set_variable(domain.name(), "ansible_host", addrs[0]["addr"])
                            # inventory.set_variable(domain.name(), "ansible_ssh_private_key_file", "/home/jvanz/.ssh/id_rsa_dummy")
                            inventory.set_variable(domain.name(), "ansible_user", "root")
                            inventory.set_variable(domain.name(), "ansible_ssh_pass", "root")
                            # TODO configure dinamic user
                            # inventory.set_variable(domain.name(), "ansible_ssh_common_args", f'-o ProxyCommand="ssh -W %h:%p -q root@{host}')


    def get_group(self, domain, kvmgroup):
        name = domain.name()
        for p, group in kvmgroup.items():
            if name.startswith(p):
                return  ["vms", group]


    def add_groups(self, kvmgroups, inventory):
        inventory.add_group("vms")
        for kvmgroup in kvmgroups:
            for p in kvmgroups[kvmgroup].values():
                inventory.add_group(p)
