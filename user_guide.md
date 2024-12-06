

## General Usage

The main role of the library is to provide a unified framework for easily computing a variety of statistical summaries of datasets. A number of summaries are available out of the box with pre-specified configurations, allowing a large number of results to be obtained from just a few lines of code. However, many users will require specialised results for their unique case, therefore the framework supports the addition of customised results. 

We run through possible use cases of the library, increasing the flexibility and complexity required by the user as we progress.

### Statistical Summaries

A statistical summary is comprised of two steps, computation of a statistic and a subsequent summarisation step. In many cases, these two steps are independent of one another. For example, the covariance of a dataset yields a matrix, which we can then summarise in a variety of ways including extracting eigenvalues, matrix norms or the matrix determinant. Conversely, those same summaries can be applied to any other statistic yielding a matrix. Therefore, it is possible to perform many combinations between the two.

In some cases, the statistic itself produces a scalar value, therefore performing the summary role as well. Examples include error statistics from model fits, 

The library supports the following types of statistical summary:
- Basic
- Distance
- Casual
- Information Theory
- Spectral
- Wavelet
- Miscellaneous

These types serve to roughly group statistical summaries based on expected interest of the user. A full list of the statistics available can be found in the **Available Statistical Summaries** section later in the document. 

### Standard Usage

For many purposes, existing statistical summaries and pre-defined configurations are sufficient. The user can select summaries through a range of criteria as needed. In all cases, the configuration in question can be found by running the following code, which will return the configuration YAML:

#### Specific Statistic

A specific statistic can be selected and run 

#### Statistic Type

Simply specifying the type of statistical summary will compute all statistics over a pre-defined range of parameters.


#### Statistic Theme

## Advanced Concepts

### Statistical Summaries

### Run Configurations

While instantiated statistics and summarisers can be passed to the `Calculator` class and utilised as is (with pre-defined parameters), when the parameterisation scheme becomes large it is more convenient to provide a configuration. This method is also required when utilising the distributed computing component.

Configuration can be provided in code or via a file. The required format contains one or both of the following components:

- A `Statistics` and `Summarisers` section.
- A `SummaryStatistics` section.

We consider each case in turn.

#### Statistics and Summarisers

Each *Statistic* defined under the `Statistics` section must be unique, but summarisers defined under the `Summariser` section can appear multiple times. The hierarchy for defining the scheme is as follows:

    Statistics
	    1stStatisticName
		   parameters
	    2ndStatisticName
		   parameters
	    .
	    .
	    .
	    nthStatisticName
		   parameters
	
	Summarisers
		1stSummariserName:
			Parameters:
				parameters
			Constraints:
				Statistics
		.
		.
		.
		mthSummariserName:
			.
			.
			.

Note: sectioned under `Constraints` you can find a reference to `Statistics`, which indicates that the structure within this section mirrors that of the `Statistics` section.

#### SummaryStatistics

This section essentially follows the same structure as the previous `Statistics` section: each *SummaryStatistic* added must be unique, different variants are defined via parameterisation:

    SummaryStatistics
	    1stStatisticName
		   parameters
	    2ndStatisticName
		   parameters
	    .
	    .
	    .
	    nthStatisticName
		   parameters

We now provide specifications for each supported format. Later, we will provide a motivating example to illustrate the structure further.

## Creating Custom Run Configurations

For general information on the structure of *Run Configurations* please see the **Run Configurations** section above under **Advanced Concepts**. The following sections detail how that general structure is translated into supported configuration formats.

### YAML

The *pyspi* package upon which this library is based utilised YAML files to specify various configuration parameters. We have retained this use but simplified the required format. Run configuration now only requires information relevant to statistic selection and computation. Several pre-defined YAML configuration files will be available as part of the release that can be used directly or as a baseline for tailoring your own configuration. YAML provides arguably the cleaning depiction of the required hierarchy.

#### Statistics

Each statistic specified must have a unique name. Variations of the same statistic are specified by different parameterisation schemes. Under the statistic name, a `-` symbol declares the beginning of a new parameterisation, with each subsequent line defining a configured parameter and value.

    Statistics:
	    1stStatisticName:
		    - parameter: value
		2ndStatisticName:
			- parameter_1: first_parameter_1_value
			  parameter_2: first_parameter_2_value
			- parameter_1 : second_parameter_1_value
			  parameter_2 : second_parameter_2_value
			...
			- parameter_1: mth_parameter_1_value
			- parameter_2: mth_parameter_2_value
		...
		ithStatisticName:
			- parameter_1 : value
			  parameter_2 : value
	
#### Summarisers

Summarisers are defined in a similar way, however there are some key differences as mentioned previously. Firstly, they provide an extra layer of configuration to support constraints on the statistics they're applied to in the run. Secondly, a single summariser can appear more than once unlike with statistics. This is to facilitate the possibility of constraining a certain variant of summariser to a certain variants of statistics:

	Summarisers:
		- 1stSummariserName:
			Parameters:
				- parameter_1 : value
			Constraints:
				1stStatisticName:
				2ndStatisticName:
					- parameter_1 : value
		- 1stSummariserName:
			Parameters:
				- parameter_1 : different_value
			Constraints:
				3rdStatisticName:
					- parameter_1 : value
				4thStatisticName:
					- parameter_1 : value
					- parameter_2 : value
		- 2ndSummariserName:
			- Parameters:
				- parameter_1 : value
		...
		- jthSummariserName:
			...

As indicated in the **General Structure** section, the `Constraints` section of the `Summariser` configuration follows the same structure as in `Statistics`.

#### Summary Statistics

Finally, the all-in-one summary statistics are configured under the `SummaryStatistic` section:

    SummaryStatistics:
		1stSummaryStatisticName:
			- parameter_1 : value
				  
		2ndSummaryStatisticName
			- parameter_1 : value
			- parameter_2 : value
			  ...
			- parameter_p : value
		...
		kthSummaryStatisticName:
			...

#### Running the Configuration

Once the configuration YAML is created, it can be provided to the framework either by referencing the file path:

    calc = Calculator(**calc_params)
    path = "\...\my_config_file.yaml"
    calc.set_yaml_configuration_path(path)
    results = calc.compute()

Or by via a variable, for example `run_yaml`, containing the YAML string:

    calc = Calculator(**calc_params)
    calc.set_yaml_configuration(run_yaml)
    results = calc.compute()

For most use cases, the path method will be sufficient. However, providing a variable containing YAML is convenient when building a run configuration programmatically.

### JSON

JSON files specify the configuration in a very similar fashion, albeit with the popular JSON format. While slightly longer than the YAML configuration, JSON has the advantage of being naturally comparable to the Python dictionary object

#### Statistics

The general format for the `Statistics` object is as below

    {
	    "Statistics" : {
		    "1stStatisticName" : {
		    }
	    }
	}



#### Summarisers
#### SummaryStatistics

#### Running the Configuration

Once the configuration JSON is created, it can be provided to the framework either by referencing the file path:

    calc = Calculator(**calc_params)
    path = "\...\my_config_file.json"
    calc.set_json_configuration_path(path)
    results = calc.compute()

Or provided by an in-memory variable, for example `run_json`, which may be convenient if building the JSON programmatically:

	calc = Calculator(**calc_params)
    calc.set_json_configuration(run_json)
    results = calc.compute()

### Dictionary Object

An in-memory dictionary object can be provided instead. The required structure is identical to the **JSON** provided in the above section. In fact, the `set_json_configuration()` method above simply converts the JSON string into a Python dictionary.

#### Running the Configuration

For a dictionary `run_dict` containing the run configuration, the following code will execute the required run:

    calc = Calculator(**calc_params)    
    calc.set_dict_configuration(run_dict)
    results = calc.compute()

### Motivating Example

To better describe the requirements for the run configuration, we'll provide an example applied to an $n \times p$ dataset:

#### Run Configuration

We'll derive the following general statistics:

- Statistic 1: EmpiricalCovariance [Output: $p \times p$ matrix]
- Statistic 2: EllipticEnvelope [Output: $p \times p$ matrix]
	- Variant: Squared
- Statistic 3: PairwiseDistance [Output: $n \times n$ matrix]
	- Variant: Euclidean
- Statistic 4: InformationGeometricConditionalIndependence (ICGI) - [Output: $p \times p$ matrix]
	- Variant: Variables
- Statistic 5: InformationGeometricConditionalIndependence (ICGI) - [Output: $n \times n$ matrix]
	- Variant: Observations

Apply the following summaries to these statistics:

- Summariser 1: MatrixDeterminant [Output: $5$-vector]
	- Variants: Scaled
	- Statistics: All Except 5
- Summariser 2: Moments [Output: $6$-vector ($3$ moments for $2$ statistics)]
	- Selection: First 3
	- Statistics: 3, 5

And finally include the following fully defined summary statistics:
- SummaryStatistic 1: PCAVarianceExplained [Output: $2$-vector]
	- Selection: First 2
- SummaryStatistic 2: PCALoadings; [Output: $2p$-vector ($2$ loadings for $p$ variables)]
	- Selection: First 2

Total number of summary scalars: $13 + 2p$. Thus the output from this scheme will be a single row-wise $(13 + 2p)$-vector as a numpy array. 

#### YAML File

Firstly, we create the YAML configuration file as below:

	Statistics:
	    EmpiricalCovariance:
	    EllipticEnvelope:
		    - squared: True
	    PairwiseDistance:
		    - metric: "euclidean"
	    IGCI:
		    - transpose: False
		    - transpose: True
	    
    Summarisers:			
		- MatrixDeterminant:
			Parameters:
				- scaled: True
			Constraints:
				¬IGCI
					-transpose: False
		- Moments:
			Parameters:
				- first: 3
			Constraints:
				PairwiseDistance
				IGCI:
					- transpose: True

	SummaryStatistics:
	    PCAVarianceExplained:
		    Parameters:
			    - first: 2
	    PCALoadings:
		    Parameters:
			    - first: 2

Next, we save the file as a simple text file at the path `C:\TestRuns\MyYamlConfiguration.yaml`.

Finally, in Python, we execute the following code:

    from pyspc import Calculator

	calc = Calculator(**calc_params)
	yaml_path = "C:/TestRuns/MyYamlConfiguration.yaml"
	calc.set_yaml_configuration_path(yaml_path)
	result = calc.compute()	


#### JSON File

    {
	    "Statistics" : {
		    "EmpiricalCovariance" : [],
		    "EllipticEnvelope" : [
			    {"squared" : true}
			],
		    "PairwiseDistance": [
			    {"metric" : "euclidean"}
			],
		    "IGCI": [
			    {"tranpose" : false}, 
			    {"transpose" : true}
			]
		},
	    
	    "Summaries": {		    
			"MatrixDeterminant": {
				"Parameters" : [
					{"scaled": true}
				],
				"Constraints" : {
					"¬ICGI" : [
						{"transpose" : false}
					]
				}
			},
			"Moments": {
				"Parameters" : [
					{"first": 3}
				],
				"Constraints" : {
					"PairwiseDistance" : []
					"IGCI" : [
						{"transpose" : true}
					]					
				}
			}
		},

		"SummaryStatistics":
			"PCAVarianceExplained": {
			    "Parameters": [
					{"first": 2}
				]
			},
		    "PCALoadings": {
			    "Parameters" : [
					{"first": 2}
				]
			}
		}
	}


#### Important Notes

- The `Constraints` subsection under each Summariser limits the application of the Summariser to specific Statistics. 
- Specific parameterised statistic variants are referenced through the same structure present in the `Statistics` section. 
- If no parameters are specified for a Statistic in the `Constraints` section, this is treated as the entire configuration for that Statistic.
- The not sign `¬` is used in the `Constrants` section to indicate all except a particular statistic. This can be seen under the `MatrixDeterminant` summary constraints for `ICGI`.



## Defining Custom Statistics and Summarisers

In line with the statistical summary flow described in the **Section** section, there two ways of defining the *Statistic* and *Summariser* combination: some *Statistics* and *Summarisers* are independent of one another,  In other cases, a Statistic and Summariser will be very specifically tied together, in which case we define them as a single entity.

### Generalised Flow:

In this case, either a custom Statistic is defined or a Summariser (or both!), there need not be any link between them. In either case, the defined object must inherit from the applicable *pyspc* base object.

#### Statistic

The custom *Statistic* inherits from the base `Statistic` class and **must** implement the `compute()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import Statistic
    
    class MyStatistic(Statistic):
    
	    def __init__(self, stat_param_1, stat_param_2, ..., stat_param_n):
		    ... implemented code ...
		    
		def compute() -> np.ndarray:
			... implemented code ...
			return np.ndarray

#### Summarizer

Similar to the custom *Statistic* class, the custom *Summariser* inherits from the base `Summariser` class and **must** implement the `summarise()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import Summariser
    
    class MySummariser(Summariser):
    
	    def __init__(self, summary_param_1, summary_param_2, ..., summary_param_m):
		    ... implemented code ...
		    
		def summarise() -> np.ndarray:
			... implemented code ...
			return np.ndarray

### All in One:

For *Statistics* and *Summarisers* that need to be paired together specifically, an all in one class called *SummaryStatistic* can be used instead which performs both the statistic computation and summarisation in one shot. The custom object inherits from the base `SummaryStatistic` class and **must* implement the `summarise()` method, returning a numpy array (type `np.ndarray`):

    from pyspc import SummaryStatistic
    
    class MySummaryStatistic(SummaryStatistic):
    
	    def __init__(self, 
		    stat_param_1, 
		    stat_param_2, 
		    ..., 
		    stat_param_n,
		    summary_param_1,
		    summary_param_2,
		    ...,
		    summary_param_m):
		    
		    ... implemented code ...
		    
		def summarise() -> np.ndarray:
			... implemented code ...
			return np.ndarray
			
The main distinction from the **Generalised Flow** is that a *SummaryStatistic* is self contained and will not be subjected to summarisation from other registered *Summariser* objects by the *Calculator* class.

### Registering Custom Objects

Once custom objects are defined, they need to be registered for use with the applicable `Calculator` object. Registry can be performed in a variety of ways depending on the use case:

#### Specific Instances

A specific instance of the object with parameters pre-defined can be registered:

    calc = Calculator(**calc_params)
    my_stat = MyStatistic(**statistic_params)
    my_summarizer = MySummariser(**summary_params)
    my_summary_stat = MySummaryStatistic(**statistic_params, **summary_params)
    calc.register_custom_object(my_stat)
    calc.register_custom_object(my_summarizer)
    calc.register_custom_object(my_summary_stat)

As these are instances of the custom object, their parameters are now set in stone and will not be altered when `Calculator.compute()`  is called. This can be useful for testing or small scale analysis but we may want a range of parameter specifications to be applied from a configuration specification.

#### General Objects
If we want parameterization to be applied in a configurable manner, we instead simply register the object itself:

    calc = Calculator(**calc_params)
    calc.register_custom_class(MyStatistic)
    calc.register_custom_class(MySummariser)
    calc.register_custom_class(MySummaryStatistic)

Now the classes will be made available for parameter injection from configuration specification instead.

### Grouping
If a higher quantity of custom statistics and/or summarisers are defined, it could be laborious to register them all individually. In this case, they can be registered en mass in a number of ways:

#### Iterable
Simply provide an iterable containing the objects in question. For specific instances:

    calc = Calculator(**calc_params)
    stat_1 = MyStatistic1(**stat_params_1)
    stat_2 = MyStatistic2(**stat_params_2)
    summariser = MySummariser(**summary_params)
    summary_stat = MySummaryStatistic(**summary_stat_params)
    custom_objects = [stat_1, stat_2, summariser, summary_stat]
    calc.register_custom_objects(custom_objects)

And for general classes open to configurable parameterisation:

    calc = Calculator(**calc_params)
    custom_classes = [MyStatistic1, MyStatistic2, MySummariser, MySummaryStatistic]
    calc.register_custom_classes(custom_classes)

This is useful when the number of objects is moderate. However, if a large number of objects are required - or one does not wish to load them all into memory - a better method is to register a module.

#### Module
An imported module can be registered in one command. However, note that this method does not allow for the definition of instantiated objects with pre-define parameters.

    import custom_stats
    calc = Calculator(**calc_params)
    calc.register_module(custom_stats)

All objects of the relevant type will be imported. Parameterisation must then come from an associated configuration file, instead. Finally, an option exists to perform this task without importing:

#### Python File

Similar to providing a module, one can simply provide the path to Python module file instead:

    calc = Calculator(**calc_params)
    path_to_module = "C:\...\custom_stats.py"
    calc.register_module_path(path_to_module)

The same method of extracting all objects of the relevant type will be applied as in **Module** example.
