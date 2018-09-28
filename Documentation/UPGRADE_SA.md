# Upgrading a Standalone Deployment with Metro&#198;
## Prerequisites / Requirements / Notes
Before upgrading any components, you must have previously [set up your MetroÆ environment](SETUP.md) and [customized the upgrade environment for your target platform](CUSTOMIZE.md).

Ensure that you have added upgrade.yml to your deployment and specified `upgrade_from_version` and `upgrade_to_version`. MetroÆ uses these values to determine whether it is to perform a major upgrade or a minor upgrade. Failure to populate these variables could cause a minor upgrade to be treated as a major upgrade which results in the task being stuck in turn-on-api (which should not be executed for minor upgrades).

By default, the special enterprise called Shared Infrastructure is created on the VSD. When putting domains in maintenance mode prior to an upgrade, MetroÆ skips Shared Infrastructure domains because they cannot be modified.

## Example Deployment
For this example, our standalone (SA) deployment consists of:
* one VSD node
* one VSC node
* VRS instance(s)
* one VSTAT (Elasticsearch) node

## Upgrading Automatically
If your topology does not include VRS you can upgrade everything with one command. If it does includes VRS you can upgrade everything with two commands. MetroÆ also gives you the option of upgrading individual components with a single command for each. If you prefer to have more control over each step in the upgrade process proceed to [Upgrading By Individual Steps](#upgrading-by-individual-steps) for instructions.

### Upgrade All Components (without VRS)

     metroae upgrade_everything -vvv

Issuing this workflow will detect if components are clustered (HA) or not and will upgrade all components that are defined in the deployment.  This option does not pause until completion to allow VRS(s) to be upgraded.  If VRS(s) need to be upgraded, the following option should be performed instead.

### Upgrade All Components (with VRS)

     metroae upgrade_before_vrs -vvv

     ( Upgrade the VRS(s) )

     metroae upgrade_after_vrs -vvv

Issuing the above workflows will detect if components are clustered (HA) or not and will upgrade all components that are defined in the deployment.  This option allows the VRS(s) to be upgraded in-between other components.

### Upgrade Individual Components

     metroae vsp_preupgrade_health -vvv

     metroae upgrade_vsds -vvv

     metroae upgrade_vscs_before_vrs -vvv

     ( Upgrade the VRS(s) )

     metroae upgrade_vscs_after_vrs -vvv

     metroae upgrade_vstats -vvv

     metroae vsp_upgrade_postdeploy -vvv

     metroae vsp_postupgrade_health -vvv

Issuing the above workflows will detect if components are clustered (HA) or not and will upgrade all components that are defined in the deployment.  This option allows the VRS(s) to be upgraded in-between other components.  Performing individual workflows can allow specific components to be skipped or upgraded at different times.

## Upgrading By Individual Steps
The following workflows will upgrade each component in individual steps.  The steps listed below are only applicable for stand-alone (SA) deployments.  Performing an upgrade in this way allows full control of the timing of the upgrade process.

### Preupgrade Preparations
1. Run health checks on VSD, VSC and VSTAT.

     `metroae vsp_preupgrade_health -vvv`

     Check the health reports carefully for any reported errors before proceeding. You can run health checks at any time during the upgrade process.

2. Backup the VSD node database.

     `metroae vsd_sa_upgrade_database_backup -vvv`

    The VSD node database is backed up.

    **Troubleshooting**: If you experience a failure you can re-execute the command.

### Upgrade VSD

1. Power off the VSD node.

     `metroae vsd_sa_upgrade_shutdown -vvv`

     VSD is shut down; it is not deleted. (The new node is brought up with the `upgrade_vmname` you previously specified.) You have the option of powering down VSD manually instead.

     **Troubleshooting**: If you experience a failure you can re-execute the command or power off the VM manually.

2. Predeploy the new VSD node.

     `metroae vsd_predeploy -vvv`

     The new VSD node is now up and running; it is not yet configured.

     **Troubleshooting**: If you experience a failure, delete the new node by executing the command `metroae vsd_sa_upgrade_destroy`, then re-execute the predeploy command. Do NOT run `vsd_destroy` as this command destroys the "old" VM which is not what we want to do here.

3. Deploy the new VSD node.

     `metroae vsd_sa_upgrade_deploy -vvv`

     The VSD node is upgraded.

     **Troubleshooting**: If you experience a failure before the VSD install script runs, re-execute the command. If it fails a second time or if the failure occurs after the VSD install script runs, destroy the VMs (either manually or with the command `metroae vsd_sa_upgrade_destroy`) then re-execute the deploy command. Do NOT run `vstat_destroy` for this step.

4. Set the VSD upgrade complete flag.

     `metroae vsd_upgrade_complete -vvv`

     The upgrade flag is set to complete.

     **Troubleshooting**: If you experience a failure, you can re-execute the command.

5. Log into the VSD and verify the new version.

### Upgrade VSC
This example is for one VSC node. If your topology has more than one VSC node, proceed to the **Upgrade VSC Node One** section of  [UPGRADE_HA.md](UPGRADE_HA.md) and follow those instructions through to the end.

1. Run VSC health check (optional).

     `metroae vsc_health -e report_filename=vsc_preupgrade_health.txt -vvv`

     You performed health checks during preupgrade preparations, but it is good practice to run the check here as well to make sure the VSD upgrade has not caused any problems.

2. Backup and prepare the VSC node.

     `metroae vsc_sa_upgrade_backup_and_prep -vvv`

     **Troubleshooting**: If you experience failure, you can re-execute the command.

3. Deploy VSC.

     `metroae vsc_sa_upgrade_deploy -vvv`

     The VSC is upgraded.

     **Troubleshooting**: If you experience a failure, you can re-execute the command. If it fails a second time, manually copy a valid .tim file to the VSC to affect the deployment. If that fails, deploy a new VSC using the old version, or recover the VM from a backup. You can use MetroÆ for the deployment (vsc_predeploy, vsc_deploy, vsc_postdeploy...).

4. Run VSC postdeploy.

     `metroae vsc_sa_upgrade_postdeploy -vvv`

     VSC upgrade is complete.

     **Troubleshooting**: If you experience a failure, you can re-execute the command. If it fails a second time, manually copy a valid .tim file to the VSC to affect the deployment. If that fails, deploy a new VSC using the old version, or recover the VM from a backup. You can use MetroÆ for the deployment (vsc_predeploy, vsc_deploy, vsc_postdeploy...).

### Upgrade VRS
Upgrade your VRS(s) and then continue with this procedure. Do not proceed without completing this step.

### Upgrade VSTAT
Our example includes a VSTAT node. If your topology does not include one, proceed to *Finalize the Upgrade* below.

1. Run VSTAT health check (optional).

     `metroae vstat_health -e report_filename=vstat_preupgrade_health.txt -vvv`

     You performed health checks during preupgrade preparations, but it is good practice to run the check here as well to make sure the VSD upgrade has not caused any problems.

2. Backup the VSTAT node.

     `metroae vstat_upgrade_data_backup -vvv`

     Data from the VSTAT node is backed up in the NFS shared folder.

     **Troubleshooting**: If you experience a failure, you can re-execute the command.

3. Power off the VSTAT node.

     `metroae vstat_destroy -vvv`

     VSTAT shuts down; it is not deleted. (The new node will be brought up with the new VM name.) You have the option of performing this step manually instead.

     **Troubleshooting**:If you experience a failure you can re-execute the command or power off the VM manually.

4. Predeploy the new VSTAT node.

     `metroae vstat_predeploy -vvv`

     The new VSD node is now up and running; it is not yet configured.

     **Troubleshooting**: If you experience a failure, delete the new node by executing the command `metroae vstat_upgrade_destroy` then re-execute the predeploy command. Do NOT run `vstat_destroy` for this step.

5. Deploy the new VSTAT node.

     `metroae vstat_deploy -vvv`

     The new VSTAT node has been deployed and configured to talk with the VSD node.

     **Troubleshooting**: If you experience a failure, re-execute the command. If it fails a second time, destroy the VMs (either manually or with the command `metroae vstat_upgrade_destroy`) then proceed from the predeploy step above. Do NOT run `vstat_destroy` for this step.

6. Migrate data to new VSTAT node.

     `metroae vstat_upgrade_data_migrate -vvv`

     The data from the old VSTAT node is migrated to the new VSTAT node from the NFS shared folder.

     **Troubleshooting**: If you experience a failure, you can re-execute the command.

### Finalize the Upgrade
1. Finalize the settings.

     `metroae vsp_upgrade_postdeploy -vvv`

     The final steps for the upgrade are executed.

     **Troubleshooting**: If you experience a failure, you can re-execute the command.

2. Run a health check.

     `metroae vsp_postupgrade_health -vvv`

     Health reports are created that can be compared with the ones produced during preupgrade preparations. Investigate carefully any errors or discrepancies.

## Questions, Feedback, and Contributing
Ask questions and get support via the [forums](https://devops.nuagenetworks.net/forums/) on the [MetroÆ site](https://devops.nuagenetworks.net/).  
You may also contact us directly.  
  Outside Nokia: [devops@nuagenetworks.net](mailto:deveops@nuagenetworks.net "send email to nuage-metro project")  
  Internal Nokia: [nuage-metro-interest@list.nokia.com](mailto:nuage-metro-interest@list.nokia.com "send email to nuage-metro project")

Report bugs you find and suggest new features and enhancements via the [GitHub Issues](https://github.com/nuagenetworks/nuage-metro/issues "nuage-metro issues") feature.

You may also [contribute](../CONTRIBUTING.md) to MetroÆ by submitting your own code to the project.