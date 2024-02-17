<?php
    date_default_timezone_set('America/Los_Angeles');
    define('KB', 1024);

    function ECHO_RESPONSE($success, $info, $data = array()) {
        $resultArray = array('success' => $success, 'info' => $info, 'data' => $data);
        header('Content-Type: application/json');
        echo json_encode($resultArray);
        exit();
    }

    function ARRAY_HAS_VALUES_FOR_KEYS($array, $keys) {
        foreach ($keys as $key) {
            if (!array_key_exists($key, $array)) return false;
        }
        return true;
    }

    $serverName = "localhost";
    $username = "christof_labuser";
    $password = "ATPisC10H16N5O13P3";
    $queueTableName = 'zic_philic_master_ms1_mets_to_add';
    $GLOBAL_EDIT_KEY = 'timmy';

    try {
        $dbConnection = new PDO("mysql:host=$serverName;dbname=christof_labdata", $username, $password);
    } catch(PDOException $e) {
        echoResponse(false, 'Database connection error: ' . $e->getMessage());
    }

    if(isset($_POST['action'])){
        $action = $_POST['action'];

        switch($action) {
            case 'addnewmetabolite':
                $requiredKeys = ['lab_name', 'submitter_name', 'metabolite_name', 'formula', 'pubchem_id', 'kegg_id'];
                if(ARRAY_HAS_VALUES_FOR_KEYS($_POST, $requiredKeys)){
                    $stmt = $dbConnection->prepare("INSERT INTO $queueTableName (submitter_lab, submitter_name, name, formula, pubchem_id, kegg_id, status) VALUES (:labName, :submitterName, :metaboliteName, :formula, :pubchemId, :keggId, 'to be ordered')");

                    // Bind parameters
                    $stmt->bindParam(':labName', $_POST['lab_name']);
                    $stmt->bindParam(':submitterName', $_POST['submitter_name']);
                    $stmt->bindParam(':metaboliteName', $_POST['metabolite_name']);
                    $stmt->bindParam(':formula', $_POST['formula']);
                    $stmt->bindParam(':pubchemId', $_POST['pubchem_id']);
                    $stmt->bindParam(':keggId', $_POST['kegg_id']);

                    // Execute and respond
                    try {
                        $stmt->execute();
                        ECHO_RESPONSE(true, 'New metabolite added successfully.');
                    } catch(PDOException $e) {
                        ECHO_RESPONSE(false, 'Failed to add new metabolite: ' . $e->getMessage());
                    }
                } else {
                    ECHO_RESPONSE(false, 'Missing required fields');
                }
                break;

                case 'getmetabolites':
                    try {
                        $stmt = $dbConnection->query("SELECT * FROM $queueTableName WHERE `run` = 0");
                        $metabolites = $stmt->fetchAll(PDO::FETCH_ASSOC);
                
                        ECHO_RESPONSE(true, 'Metabolites fetched successfully', $metabolites);
                    } catch (PDOException $e) {
                        ECHO_RESPONSE(false, 'Failed to fetch metabolites: ' . $e->getMessage());
                    }
                    break;

                case 'setrundatesforsamplesets':
                    if(ARRAY_HAS_VALUES_FOR_KEYS($_POST, array('edit_key', 'data'))) {
                        $editKey = $_POST['edit_key'];
                        $data = json_decode($_POST['data'], true);
                
                        if($editKey == $GLOBAL_EDIT_KEY) {
                            foreach($data as $sampleSetData) {
                                if(isset($sampleSetData["id"]) && isset($sampleSetData["date_run"])) {
                                    try {
                                        // Prepare the update statement with a condition to ensure it only affects rows with 'run' set to 0
                                        $query = $dbConnection->prepare("UPDATE $queueTableName SET `run` = 1, `date_run` = :dr WHERE `id` = :id AND `run` = 0");
                                        $dateRun = date('Y-m-d H:i:s', strtotime($sampleSetData["date_run"]));
                                        $query->bindParam(':dr', $dateRun, PDO::PARAM_STR); 
                                        $query->bindParam(':id', $sampleSetData["id"], PDO::PARAM_INT); 
                                        $query->execute();
                                    } catch(PDOException $e) {
                                        ECHO_RESPONSE(false, 'database_error', 'Detailed Message: ' . $e->getMessage());
                                    }
                                } else {
                                    ECHO_RESPONSE(false, 'missing_info_error', 'Missing ID or run date in one of the sample set data arrays.');
                                }
                            }
                            ECHO_RESPONSE(true, 'sample_set_runtimes_were_updated');
                        } else {
                            ECHO_RESPONSE(false, 'permission_error', 'The provided edit key does not match the global edit key.');
                        }
                    } else {
                        ECHO_RESPONSE(false, 'missing_info_error', 'The required edit key or data was not provided.');
                    }
                    break;

            default:
                ECHO_RESPONSE(false, 'Invalid action specified');
                break;
        }
    } else {
        ECHO_RESPONSE(false, 'No action specified');
    }
?>