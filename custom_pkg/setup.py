from setuptools import setup
from glob import glob


package_name = 'custom_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your@email.com',
    description='Custom point cloud saver',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'save_pointcloud_service = custom_pkg.save_pointcloud_service:main',
            'measure = custom_pkg.measure:main',
        ],
    },
)
